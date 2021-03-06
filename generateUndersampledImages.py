#coding=utf8

########################################################################
###                                                                  ###
### Created by Martin Genet, 2012-2016                               ###
###                                                                  ###
### University of California at San Francisco (UCSF), USA            ###
### Swiss Federal Institute of Technology (ETH), Zurich, Switzerland ###
### École Polytechnique, Palaiseau, France                           ###
###                                                                  ###
########################################################################

import numpy
import vtk

import myVTKPythonLibrary as myVTK

########################################################################

def generateUndersampledImages(
        images,
        structure,
        texture,
        noise,
        deformation,
        evolution,
        undersampling_level,
        keep_temporary_images=0,
        verbose=0):

    myVTK.myPrint(verbose, "*** generateUndersampledImages ***")

    images_basename = images["basename"]
    images_n_voxels = images["n_voxels"][:]

    images["n_voxels"][1] /= undersampling_level
    if (images["n_dim"] >= 3):
        images["n_voxels"][2] /= undersampling_level
    images["basename"] = images_basename+"-X"
    texture["type"] = "taggX"
    myVTK.generateImages(
        images=images,
        structure=structure,
        texture=texture,
        noise=noise,
        deformation=deformation,
        evolution=evolution,
        verbose=verbose-1)
    images["n_voxels"] = images_n_voxels[:]
    images["basename"] = images_basename

    images["n_voxels"][0] /= undersampling_level
    if (images["n_dim"] >= 3):
        images["n_voxels"][2] /= undersampling_level
    images["basename"] = images_basename+"-Y"
    texture["type"] = "taggY"
    myVTK.generateImages(
        images=images,
        structure=structure,
        texture=texture,
        noise=noise,
        deformation=deformation,
        evolution=evolution,
        verbose=verbose-1)
    images["n_voxels"] = images_n_voxels[:]
    images["basename"] = images_basename

    if (images["n_dim"] >= 3):
        images["n_voxels"][0] /= undersampling_level
        images["n_voxels"][1] /= undersampling_level
        images["basename"] = images_basename+"-Z"
        texture["type"] = "taggZ"
        myVTK.generateImages(
            images=images,
            structure=structure,
            texture=texture,
            noise=noise,
            deformation=deformation,
            evolution=evolution,
            verbose=verbose-1)
        images["n_voxels"] = images_n_voxels
        images["basename"] = images_basename

    if ("zfill" not in images.keys()):
        images["zfill"] = len(str(images["n_frames"]))
    for k_frame in xrange(images["n_frames"]):
        imageX = myVTK.readImage(
            filename=images["folder"]+"/"+images["basename"]+"-X_"+str(k_frame).zfill(images["zfill"])+".vti",
            verbose=verbose-1)
        interpolatorX = myVTK.createImageInterpolator(
            image=imageX,
            verbose=verbose-1)
        iX = numpy.empty(1)

        imageY = myVTK.readImage(
            filename=images["folder"]+"/"+images["basename"]+"-Y_"+str(k_frame).zfill(images["zfill"])+".vti",
            verbose=verbose-1)
        interpolatorY = myVTK.createImageInterpolator(
            image=imageY,
            verbose=verbose-1)
        iY = numpy.empty(1)

        if (images["n_dim"] == 2):
            imageXY = vtk.vtkImageData()
            imageXY.SetExtent([0, images["n_voxels"][0]-1, 0, images["n_voxels"][1]-1, 0, 0])
            imageXY.SetSpacing([images["L"][0]/images["n_voxels"][0], images["L"][1]/images["n_voxels"][1], 1.])
            imageXY.SetOrigin([images["L"][0]/images["n_voxels"][0]/2, images["L"][1]/images["n_voxels"][1]/2, 0.])
            if (vtk.vtkVersion.GetVTKMajorVersion() >= 6):
                imageXY.AllocateScalars(vtk.VTK_FLOAT, 1)
            else:
                imageXY.SetScalarTypeToFloat()
                imageXY.SetNumberOfScalarComponents(1)
                imageXY.AllocateScalars()
            scalars = imageXY.GetPointData().GetScalars()
            x = numpy.empty(3)
            for k_point in xrange(imageXY.GetNumberOfPoints()):
                imageXY.GetPoint(k_point, x)
                interpolatorX.Interpolate(x, iX)
                interpolatorY.Interpolate(x, iY)
                scalars.SetTuple(k_point, (iX*iY)**(1./2))
            myVTK.writeImage(
                image=imageXY,
                filename=images["folder"]+"/"+images["basename"]+"_"+str(k_frame).zfill(images["zfill"])+".vti",
                verbose=verbose-1)
            if not (keep_temporary_images):
                os.system("rm "+images["folder"]+"/"+images["basename"]+"-X_"+str(k_frame).zfill(images["zfill"])+".vti")
                os.system("rm "+images["folder"]+"/"+images["basename"]+"-Y_"+str(k_frame).zfill(images["zfill"])+".vti")

        elif (images["n_dim"] == 3):
            imageZ = myVTK.readImage(
                filename=images["folder"]+"/"+images["basename"]+"-Z_"+str(k_frame).zfill(images["zfill"])+".vti",
                verbose=verbose-1)
            interpolatorZ = myVTK.createImageInterpolator(
                image=imageZ,
                verbose=verbose-1)
            iZ = numpy.empty(1)

            imageXYZ = vtk.vtkImageData()
            imageXYZ.SetExtent([0, images["n_voxels"][0]-1, 0, images["n_voxels"][1]-1, 0, images["n_voxels"][2]-1])
            imageXYZ.SetSpacing([images["L"][0]/images["n_voxels"][0], images["L"][1]/images["n_voxels"][1], images["L"][2]/images["n_voxels"][2]])
            imageXYZ.SetOrigin([images["L"][0]/images["n_voxels"][0]/2, images["L"][1]/images["n_voxels"][1]/2, images["L"][2]/images["n_voxels"][2]/2])
            if (vtk.vtkVersion.GetVTKMajorVersion() >= 6):
                imageXYZ.AllocateScalars(vtk.VTK_FLOAT, 1)
            else:
                imageXYZ.SetScalarTypeToFloat()
                imageXYZ.SetNumberOfScalarComponents(1)
                imageXYZ.AllocateScalars()
            scalars = imageXYZ.GetPointData().GetScalars()
            x = numpy.empty(3)
            for k_point in xrange(imageXYZ.GetNumberOfPoints()):
                imageXYZ.GetPoint(k_point, x)
                interpolatorX.Interpolate(x, iX)
                interpolatorY.Interpolate(x, iY)
                interpolatorZ.Interpolate(x, iZ)
                scalars.SetTuple(k_point, (iX*iY*iZ)**(1./3))
            myVTK.writeImage(
                image=imageXYZ,
                filename=images["folder"]+"/"+images["basename"]+"_"+str(k_frame).zfill(images["zfill"])+".vti",
                verbose=verbose-1)
            if not (keep_temporary_images):
                os.system("rm "+images["folder"]+"/"+images["basename"]+"-X_"+str(k_frame).zfill(images["zfill"])+".vti")
                os.system("rm "+images["folder"]+"/"+images["basename"]+"-Y_"+str(k_frame).zfill(images["zfill"])+".vti")
                os.system("rm "+images["folder"]+"/"+images["basename"]+"-Z_"+str(k_frame).zfill(images["zfill"])+".vti")

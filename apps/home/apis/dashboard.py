from django.views.generic import View
from django.http import JsonResponse
from core.settings import BASE_DIR
from tensorflow.keras.models import load_model
import base64
import cv2
from deepbet import run_bet
import dicom2nifti
import joblib
import matplotlib
import matplotlib.pyplot as plt
import nibabel as nib
import numpy as np
import os
import pandas as pd
import random
import shutil
import string
matplotlib.use('Agg') 


class DashboardApis(View):

    @classmethod
    def slice_ct_image(cls, ct_data_path):
        """
        convert 3d ct image into 3 slices of image
        """
        img = nib.load(ct_data_path)
        image_data = img.get_fdata()
        cls.remove_temporary_ct_image(ct_data_path)
        
        axial = image_data[:, :, image_data.shape[2] // 2]
        coronal = image_data[:, image_data.shape[1] // 2, :]
        sagittal = image_data[image_data.shape[0] // 2, :, :]

        x_dim, y_dim, _ = img.header.get_zooms()
        aspect_ratio = y_dim / x_dim

        file_name = ct_data_path.split('/')[-1].split('.')[0]
        output_path = BASE_DIR + '/temporary_ct_data/slices/' + file_name

        cls.save_slice_image(sagittal, aspect_ratio, 200, output_path + '_sagittal.png')
        cls.save_slice_image(coronal, aspect_ratio, 200, output_path + '_coronal.png')
        cls.save_slice_image(axial, aspect_ratio, 200, output_path + '_axial.png')

        return cls.load_slice_image(file_name)
    
    @classmethod
    def save_slice_image(cls, slice_image, ratio, dpi, output_path):
        plt.figure(figsize=(8, 8 * ratio), dpi=dpi)
        plt.imshow(slice_image.T, cmap='gray', origin='lower', aspect='auto')
        plt.axis('off')
        plt.savefig(output_path, bbox_inches='tight', pad_inches=0, dpi=dpi)
        plt.close()

    @classmethod
    def load_slice_image(cls, img_name):
        
        dir_file = BASE_DIR + '/temporary_ct_data/slices/' + img_name
        axial = cv2.imread(dir_file + '_axial.png', 0)
        coronal = cv2.imread(dir_file + '_coronal.png', 0)
        sagittal = cv2.imread(dir_file + '_sagittal.png', 0)
        
        _, buffer = cv2.imencode('.png', axial)
        axial_base64 =  base64.b64encode(buffer).decode('utf-8')

        _, buffer = cv2.imencode('.png', coronal)
        coronal_base64 =  base64.b64encode(buffer).decode('utf-8')

        _, buffer = cv2.imencode('.png', sagittal)
        sagittal_base64 =  base64.b64encode(buffer).decode('utf-8')

        axial = cv2.resize(axial, (100, 100))
        coronal = cv2.resize(coronal, (100, 100))
        sagittal = cv2.resize(sagittal, (100, 100))
        axial = axial.astype('float32')
        axial = (axial / 255.0).flatten()
        coronal = coronal.astype('float32')
        coronal = (coronal / 255.0).flatten()
        sagittal = sagittal.astype('float32')
        sagittal = (sagittal / 255.0).flatten()

        cls.remove_temporary_ct_image(dir_file + '_axial.png')
        cls.remove_temporary_ct_image(dir_file + '_coronal.png')
        cls.remove_temporary_ct_image(dir_file + '_sagittal.png')


        return [axial], [coronal], [sagittal], \
            axial_base64, coronal_base64, sagittal_base64

    @classmethod
    def normalize_image(cls, ct_data_path):
        # load models
        ae_load_model = load_model(BASE_DIR +  '/apps/ml_model/autoencoder/v1.h5')
        mm_load_model = joblib.load(BASE_DIR +  '/apps/ml_model/autoencoder/v1.joblib')
        axial, coronal, sagittal, axial_base64, coronal_base64, \
            sagittal_base64 = cls.slice_ct_image(ct_data_path)
        
        axial = mm_load_model.transform(axial)
        coronal = mm_load_model.transform(coronal)
        sagittal = mm_load_model.transform(sagittal)

        axial = ae_load_model.predict(axial)
        coronal = ae_load_model.predict(coronal)
        sagittal = ae_load_model.predict(sagittal)

        data = \
        {
            'ct_axial': [x[0] for x in axial.tolist()],
            'ct_coronal': [x[0] for x in coronal.tolist()],
            'ct_sagittal': [x[0] for x in sagittal.tolist()]
        }

        return pd.DataFrame(data), axial_base64, coronal_base64, sagittal_base64

    @classmethod
    def classify(cls, ct_data_path, compliment_data, model_path, model_type):        
        ml_model = joblib.load(model_path)
        ct_data, axial_base64, coronal_base64, \
            sagittal_base64 = cls.normalize_image(ct_data_path)

        if not isinstance(compliment_data, pd.DataFrame):
            compliment_data = ct_data
        else:

            compliment_data = pd.concat([compliment_data, ct_data], axis=1)
            
            if model_type == '2':
                new_column_order = ['ct_axial', 'ct_coronal', 'ct_sagittal',
                'awitan', 'usia', 'tensi_atas', 'tensi_bawah']

                compliment_data = compliment_data[new_column_order]            

        result = ml_model.predict(compliment_data)
        result_proba = ml_model.predict_proba(compliment_data)

        print(result)
        print(result_proba)

        return result[0], result_proba, axial_base64, coronal_base64, sagittal_base64
        
    @classmethod
    def post(cls, reqeuest):
        post_data = reqeuest.POST
        file_data = reqeuest.FILES.getlist('files')

        random_name = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
        
        # generate nifti file
        cls.save_temporary_dicom(file_data, random_name)
        cls.convert_dicom_to_nifti(random_name)
        cls.remove_temporary_dicom(random_name)
        cls.stripping(random_name)

        random_name = BASE_DIR + '/temporary_ct_data/nifti/' + random_name + '.nii.gz'

        compliment_data = []
        model_dir = BASE_DIR + '/apps/ml_model/random_forest/2_classes/'
        if post_data['dropdown'] != '1':
            columns = ['awitan', 'usia', 'tensi_atas', 'tensi_bawah']
            compliment_data = [post_data['awitan'], post_data['usia'],
                post_data['tensi_atas'], post_data['tensi_bawah']]
            
            if post_data['dropdown'] == '3':
                columns += ['pt', 'aptt', 'fibrinogen', 'gds']
                compliment_data += [post_data['pt'], post_data['aptt'],
                    post_data['fibrinogen'], post_data['gds']]
                model_dir += 'ct_clinic_lab/v1.joblib'
            else:
                model_dir += 'ct_clinic/v1.joblib'

            compliment_data = [int(x) for x in compliment_data]
            compliment_data = pd.DataFrame([compliment_data], columns=columns)
        else:
            model_dir += 'ct/v1.joblib'
    
        result, result_proba, axial_base64, coronal_base64, \
            sagittal_base64 = cls.classify(random_name, compliment_data,
                model_dir, post_data['dropdown'])
        
        return JsonResponse({
            'status' : 200,
            'result' : result, 
            'result_proba' : result_proba.tolist(),
            'axial_base64' : axial_base64,
            'coronal_base64' : coronal_base64,
            'sagittal_base64' : sagittal_base64
        })

    @classmethod
    def save_temporary_dicom(cls, dicom_files, name):
        # create folder for collect dicom files
        default_path = BASE_DIR + '/temporary_ct_data/dicom/' + name 
        os.makedirs(default_path, exist_ok=True)

        for idx, dicom_file in enumerate(dicom_files):
            with open(default_path + f'/{idx}.dcm', 'wb') as f:    
                f.write(dicom_file.read())
    
    @classmethod
    def remove_temporary_dicom(cls, name):
        dir_path = BASE_DIR + f'/temporary_ct_data/dicom/{name}/'
        if os.path.exists(dir_path):
            shutil.rmtree(dir_path)

    @classmethod
    def remove_temporary_ct_image(cls, ct_image_path):
        os.remove(ct_image_path)

    @classmethod
    def convert_dicom_to_nifti(cls, name):
        dicom_path = BASE_DIR + f'/temporary_ct_data/dicom/{name}/'
        nifti_path = BASE_DIR + f'/temporary_ct_data/nifti/{name}/'

        # generate nifti file
        os.makedirs(nifti_path, exist_ok=True)
        dicom2nifti.convert_directory(dicom_path, nifti_path, compression=True, reorient=True)
        
        # normalize nifti file
        nifti_file_name = os.listdir(nifti_path)[0]
        shutil.move(nifti_path + nifti_file_name, f'temporary_ct_data/nifti/{name}.nii.gz')

        # remove tmp folder
        if os.path.exists(nifti_path):
            shutil.rmtree(nifti_path)
    
    @classmethod
    def stripping(cls, name):
        nifti_path = [BASE_DIR + f'/temporary_ct_data/nifti/{name}.nii.gz']

        run_bet(nifti_path, nifti_path, threshold=.5, n_dilate=0, no_gpu=True)


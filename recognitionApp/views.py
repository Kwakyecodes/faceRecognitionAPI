from django.shortcuts import render, redirect
import face_recognition
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
import json
from PIL import Image
from .models import Item, Person
import os



# Global variables

path_to_knowns = "/Users/emmanuelkwakyenyantakyi/Desktop/cs/Python_files/Django_Projects/face_rec_api/recognitionApp/static/known_faces/"
path_to_new_face = "/Users/emmanuelkwakyenyantakyi/Desktop/cs/Python_files/Django_Projects/face_rec_api/recognitionApp/static/new_face/new.jpg"


# Function to load and learn how to recognise known image
def learn_known_face(known_image_path):
    '''
    Even if user uploads an image that contains multiple faces, this function will still work fine.
    It only learns to the first face it detects.
    '''
    img = face_recognition.load_image_file(known_image_path)
    encoding = face_recognition.face_encodings(img)[0]

    return encoding


# Function to load and learn how to recognise unknown image
def learn_unknown_face():
    '''
    This api has been built to accomodate only one face. We can't however predict human behaviour and 
    so we're conciously going to build this function so it only learns the first face it detects 
    (so as to avoid errors that might arrive if images uploaded by users contain more than 1 face)
    '''
    img = face_recognition.load_image_file(path_to_new_face)
    location = face_recognition.face_locations(img)[0]
    encoding = face_recognition.face_encodings(img, [location])

    return encoding


# Function to compare two faces(encodings actually)
def compare_faces(known_encoding, unknown_encoding):
    result = face_recognition.compare_faces(known_encoding, unknown_encoding)

    return result[0]

# Function to move image from media/images to static/new_face and be renamed new.jpg
def moveImageToStatic():
    directory = '/Users/emmanuelkwakyenyantakyi/Desktop/cs/Python_files/Django_Projects/face_rec_api/recognitionApp/media/images'
    old_path = ''
    permitted_files = ['jpg', 'png']

    # There is always going to be only one image file inside media/images
    # We only work with the file if it is an image
    for filename in os.listdir(directory):
        if (filename != '.DS_Store') and (filename[-3:] in permitted_files):
            old_path = os.path.join(directory, filename)
            break

    if old_path != '':
        os.rename(old_path, path_to_new_face)

    return

def moveFile(old_path, new_path):
    os.rename(old_path, new_path)
    return


'''
This function will render add.html where the user can input an image of a person and the their name to be added to
be added to the database. When the submit button is pressed, the image will be saved at media/images. The user will 
then be redirected to add_face function which will add the new face to the database.
'''
def upload_add(request):
    if request.method == 'POST':
        prod = Item()
        name = request.POST.get('name')
        prod.name = name
        
        if len(request.FILES) != 0:
            prod.image = request.FILES['image']

        prod.save()
        moveImageToStatic()
        return redirect(f'add/{name}')
    return render(request, 'add.html')


'''
This function will render find.html where the user can upload the image of an unknown face they want to find. Whent the
submit button is pressed, the image will be saved in media/images. The user will then be redirected to the find_face
functio which will tell them the result of the search.
'''
def upload_find(request):
    if request.method == 'POST':
        prod = Item()
        prod.name = "not_required"
        
        if len(request.FILES) != 0:
            prod.image = request.FILES['image']

        prod.save()
        moveImageToStatic()
        return redirect('find/')
    return render(request, 'find.html')


# This function clears the database
def delete(request):
    if request.method == 'GET':
        try:
            Person.objects.all().delete()
            Item.objects.all().delete()
            response = json.dumps('Deleted successfully')
        except:
            response = json.dumps('Delete unsuccessful')
        return HttpResponse(response)
 


@csrf_exempt
def add_face(request, name):
    if request.method == 'GET':

        # Load new face into variable image
        try:
            image = face_recognition.load_image_file(path_to_new_face)
        except:
            response = json.dumps('Error: No image in new_face directory')
            return HttpResponse(response)

        # Add new face to known_faces directory and update count if face already exists
        name = name.lower()
        try:
            Person.objects.get(name_of_person=name).increase_count()
            person = Person.objects.get(name_of_person=name)
            nameOfImage = f"{name}{person.count}.jpg"
            moveFile(path_to_new_face, path_to_knowns + nameOfImage)
        except:
            person = Person(name_of_person = name, count = 1)
            nameOfImage = f"{name}1.jpg"
            person.save()
            moveFile(path_to_new_face, path_to_knowns + nameOfImage)

        response = json.dumps(f'Success: New face of {name} has been added')
        return HttpResponse(response)

@csrf_exempt
def find_person(request):
    if request.method == 'GET':

        # Load new face and learn how to recognise it
        try:
            unknown_encoding = learn_unknown_face()
        except:
            response = json.dumps('Error: No image in new_face directory')
            return HttpResponse(response)

        # Verify that new face image contains at least one human face
        if unknown_encoding == []:
            response = json.dumps('Error: No face detected in image')
            return HttpResponse(response)

        # Go through persons in Person and compare new_face to all faces of all of known persons
        for person in Person.objects.all():
            isPerson = True
            name = person.name_of_person
            count = person.count 
            for i in range(1, count + 1):
                face = f"{name}{i}.jpg"
                known_encoding = learn_known_face(path_to_knowns + face)
                result = face_recognition.compare_faces(known_encoding, unknown_encoding)
                if not result[0]:
                    isPerson = False
                    break

            # If person is found, add new face of person to knowns and return name of person
            if isPerson:
                Person.objects.get(name_of_person=name).increase_count()
                image = face_recognition.load_image_file(path_to_new_face)
                nameOfImage = f"{name}{count + 1}.jpg"
                moveFile(path_to_new_face, path_to_knowns + nameOfImage)

                response = json.dumps(f"Match found. Person is {name}")
                return HttpResponse(response)
        
        response = json.dumps("No match found")
        return HttpResponse(response)



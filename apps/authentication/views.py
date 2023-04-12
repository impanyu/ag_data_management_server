# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

# Create your views here.
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from .forms import LoginForm, SignUpForm
import os
from django.conf import settings
from ..home.data import *


def login_view(request):
    form = LoginForm(request.POST or None)

    msg = None

    if request.method == "POST":

        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect("/")
            else:
                msg = 'Invalid credentials'
        else:
            msg = 'Error validating the form'

    return render(request, "accounts/login.html", {"form": form, "msg": msg})


def register_user(request):
    msg = None
    success = False

    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get("username")
            raw_password = form.cleaned_data.get("password1")
            #user = authenticate(username=username, password=raw_password)
            #create the home folder /data/username


            user_file_name = f"/data/{username}"
            user_meta_file_name = "_".join(user_file_name.split("/")[1:]) + ".json"
            data_file_name = f"/data/{username}/ag_data"
            meta_data_file_name = "_".join(data_file_name.split("/")[1:]) + ".json"
            domain_file_name = f"{data_file_name}/domain"
            domain_meta_file_name = "_".join(domain_file_name.split("/")[1:]) + ".json"

            # create user file
            if not os.path.exists(user_file_name):
                os.makedirs(user_file_name)

            # create data file
            if not os.path.exists(data_file_name):
                os.makedirs(data_file_name)

            # create domain file
            if not os.path.exists(domain_file_name):
                os.makedirs(domain_file_name)


            if not os.path.exists(os.path.join(settings.CORE_DIR, 'data', user_meta_file_name)):
                user_meta_data = generate_meta_data_for_dir(user_file_name)

            with open(os.path.join(settings.CORE_DIR, 'data','data.json'), 'r') as root_meta_data_file:
                root_meta_data = json.load(root_meta_data_file)
                if user_file_name not in root_meta_data["subdirs"]:
                    root_meta_data["subdirs"].append(user_file_name)

            with open(os.path.join(settings.CORE_DIR, 'data','data.json'), 'w') as root_meta_data_file:
                json.dump(root_meta_data, root_meta_data_file)



            if not os.path.exists(os.path.join(settings.CORE_DIR, 'data', meta_data_file_name)):
                meta_data = generate_meta_data_for_dir(data_file_name)

            if data_file_name not in user_meta_data["subdirs"]:
                user_meta_data["subdirs"].append(data_file_name)

            with open(os.path.join(settings.CORE_DIR, 'data', user_meta_file_name), 'w') as user_meta_data_file:
                json.dump(user_meta_data, user_meta_data_file)



            if not os.path.exists(os.path.join(settings.CORE_DIR, 'data', domain_meta_file_name)):
                domain_meta_data = generate_meta_data_for_dir(domain_file_name)

            if domain_file_name not in meta_data["subdirs"]:
                meta_data["subdirs"].append(domain_file_name)

            with open(os.path.join(settings.CORE_DIR,'data', meta_data_file_name), 'w') as meta_data_file:
                json.dump(meta_data,meta_data_file)



            msg = 'User created - please <a href="/login/">login</a>.'
            success = True

            # return redirect("/login/")

        else:
            msg = 'Form is not valid'
    else:
        form = SignUpForm()

    return render(request, "accounts/register.html", {"form": form, "msg": msg, "success": success})

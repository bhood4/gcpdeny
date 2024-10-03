 # Code generated via "Slingshot" 
import os
import csv
import time
from google.oauth2 import service_account
from googleapiclient.discovery import build
from google.cloud import iam, resourcemanager_v3
from google.iam.v1 import iam_policy_pb2 as iam_policy
from oauth2client.client import GoogleCredentials
from google.protobuf.json_format import MessageToDict

credentials = GoogleCredentials.get_application_default()
if credentials.create_scoped_required():
    credentials = credentials.create_scoped("https://www.googleapis.com/auth/cloud-platform")
service = build(serviceName='iam',version='v2beta',static_discovery=False)
#client = resourcemanager_v3.ProjectsClient(credentials=credentials)
cloud_resource_manager = build('cloudresourcemanager', 'v3', credentials=credentials)

def list_folders(parent):
    """
    List all folders under a given parent (organization or folder).
    """
    folders = []
    request = cloud_resource_manager.folders().list(parent=parent)
    while request is not None:
        response = request.execute()
        folders.extend(response.get('folders', []))
        request = cloud_resource_manager.folders().list_next(previous_request=request, previous_response=response)
    return folders

def list_projects(parent):
    """
    List all projects under a given parent (organization or folder).
    """
    projects = []
    request = cloud_resource_manager.projects().list(parent=parent)
    while request is not None:
        response = request.execute()
        projects.extend(response.get('projects', []))
        request = cloud_resource_manager.projects().list_next(previous_request=request, previous_response=response)
    return projects

def get_organization_folders_and_projects(organization_id):
    """
    Collect all folders and projects information for a GCP organization.
    """
    organization_name = f'organizations/{organization_id}'
    
    # List all folders under the organization
    folders = list_folders(organization_name)
    
    # List all projects under the organization
    projects = list_projects(organization_name)
    
    # List all projects under each folder
    for folder in folders:
        folder_projects = list_projects(folder['name'])
        projects.extend(folder_projects)
    
    return {
        'folders': folders,
        'projects': projects
    }

def write_to_csv(data, filename):
    """
    Write the folders and projects data to a CSV file.
    """
    with open(filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Type', 'ID', 'Name', 'Parent'])
        for folder in data['folders']:
            deny_policy = get_deny_policy(folder['name'])
            writer.writerow(['Folder', folder['name'], folder['displayName'], folder['parent'],len(deny_policy)])
        
        for project in data['projects']:
            deny_policy = get_deny_policy(project['name'])
            writer.writerow(['Project', project['projectId'], project['name'], project['parent'],len(deny_policy)])

def get_deny_policy(resource_name):
    """
    Get the IAM deny policy for a given resource (organization, folder, or project).
    """
    time.sleep(8)
    parent = f"policies/cloudresourcemanager.googleapis.com%2F{resource_name.split("/")[0]}%2F{resource_name.split("/")[1]}/denypolicies"
    response = service.policies().listPolicies(parent=parent).execute()
    return response

# Example usage
if __name__ == "__main__":
    ORGANIZATION_ID = "935878585818"
    print(get_deny_policy(f"organizations/{ORGANIZATION_ID}"))
    print(get_deny_policy("folders/415866597390"))
    print(get_deny_policy("projects/925341150427"))
    result = get_organization_folders_and_projects(ORGANIZATION_ID)
    
    # Write the result to a CSV file
    CSV_FILENAME = 'gcp_folders_projects.csv'
    write_to_csv(result, CSV_FILENAME)
    
    print(f"Data has been written to {CSV_FILENAME}")

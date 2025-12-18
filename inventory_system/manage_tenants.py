import os
import json
import argparse
import sys

# Add project root to path to allow importing from the app
project_path = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
sys.path.insert(0, project_path)

from inventory_system.config import Config


def list_tenants():
    """Lists all tenants from the tenants.json file."""
    try:
        if not os.path.exists(Config.TENANTS_FILE):
            print(f"Tenants file not found at {Config.TENANTS_FILE}")
            return
            
        with open(Config.TENANTS_FILE, 'r') as f:
            tenants_data = json.load(f)
        
        if not tenants_data:
            print("No tenants found.")
            return

        print("--- Current Tenants ---")
        for code in tenants_data.keys():
            print(f"- Access Code: {code}")

    except json.JSONDecodeError:
        print(f"Error reading tenants file. Is it a valid JSON?")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


def delete_tenant(access_code):
    """Deletes a tenant's database and removes it from tenants.json."""
    try:
        if not os.path.exists(Config.TENANTS_FILE):
            print(f"Tenants file not found at {Config.TENANTS_FILE}")
            return

        with open(Config.TENANTS_FILE, 'r') as f:
            tenants_data = json.load(f)

        if access_code not in tenants_data:
            print(f"Error: Tenant with access code '{access_code}' not found.")
            return

        db_uri = tenants_data[access_code]
        # The URI is like 'sqlite:///path/to/project/tenants/tenant_CODE.db'
        # We need to handle Windows and Unix paths correctly.
        db_path_part = db_uri.split('///')[1]
        db_path = os.path.abspath(db_path_part)

        # 1. Delete the database file
        if os.path.exists(db_path):
            os.remove(db_path)
            print(f"Successfully deleted database file: {os.path.basename(db_path)}")
        else:
            print(f"Warning: Database file not found at {db_path}, but proceeding to remove from JSON.")

        # 2. Remove from tenants data
        del tenants_data[access_code]
        
        # 3. Write the updated data back to tenants.json
        with open(Config.TENANTS_FILE, 'w') as f:
            json.dump(tenants_data, f, indent=4)
        
        print(f"Successfully removed tenant '{access_code}' from configuration.")
        print(f"Tenant '{access_code}' has been fully deleted.")

    except Exception as e:
        print(f"An error occurred: {e}")


def main():
    """Main function to parse arguments and call the appropriate function."""
    # Setting up the base directory to be the 'inventory_system' directory
    # to ensure that paths in Config are resolved correctly.
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    parser = argparse.ArgumentParser(
        description="A CLI tool to manage tenants in the inventory system."
    )
    subparsers = parser.add_subparsers(dest='command', required=True, help="Available commands")

    # 'list' command
    list_parser = subparsers.add_parser(
        'list', 
        help="List all existing tenants by their access code."
    )

    # 'delete' command
    delete_parser = subparsers.add_parser(
        'delete',
        help="Delete a tenant, including their database."
    )
    delete_parser.add_argument(
        'access_code',
        type=str,
        help="The access code of the tenant to delete."
    )
    delete_parser.add_argument(
        '--force',
        action='store_true',
        help="Force deletion without asking for confirmation. Use with caution."
    )

    args = parser.parse_args()

    if args.command == 'list':
        list_tenants()
    elif args.command == 'delete':
        if not args.force:
            print(f"\nWARNING: This is a destructive operation.")
            print(f"To permanently delete tenant '{args.access_code}' and all its data, run the command again with the --force flag.")
            return
        
        delete_tenant(args.access_code)

if __name__ == '__main__':
    main()

from daytona import Daytona, DaytonaConfig, CreateSandboxFromSnapshotParams
import requests
import os
from dotenv import load_dotenv

# This class create the cloud computer that will be used to create and edit the server
class Computer:
    load_dotenv()
    __api_key = os.getenv("DAYTONA_API_KEY")

    # Create the computer on init
    def __init__(self):
        # Create config
        config = DaytonaConfig(api_key=self._Computer__api_key)

        # Create client and parameters
        daytona = Daytona(config)
        params = CreateSandboxFromSnapshotParams(
            ephemeral=True,
            snapshot="daytona-small"
        )

        # Create computer
        self.computer = daytona.create(params)

        # Setup folder
        self.computer.process.exec("mkdir /home/daytona/minecraft-server")

        # Download and set up server.jar
        response = requests.get("https://fill-data.papermc.io/v1/objects/4c734aeb4da98845934af1e5481f0df7c80ad3ca50d272319ffe2b0e8a187c8a/paper-26.3-249.jar", timeout=120)
        response.raise_for_status()

        with open("server.jar", "wb") as f:
            f.write(response.content)

        # Upload to the computer
        self.computer.fs.upload_file("server.jar", "/home/daytona/minecraft-server/server.jar")

        # Create plugins folder
        self.computer.process.exec("mkdir /home/daytona/minecraft-server/plugins")

        print("<COMPUTER> Computer successfully started")

    # Run a command on the computer
    def run_command(self, command:str):
        response = self.computer.process.exec(command)
        print("<COMPUTER> [Command Run Output]: " + response.result)
        return response.result

    # Uploads plugin jar into the computer
    def upload_plugin(self, url:str):
        response = requests.get(url, timeout=120)
        response.raise_for_status()
        
        with open(url.rsplit('/', 1)[-1], "wb") as f:
            f.write(response.content)
        
        self.computer.fs.upload_file(url.rsplit('/', 1)[-1], "/home/daytona/minecraft-server/plugins/" + url.rsplit('/', 1)[-1])
        

    def delete_computer(self):
        self.computer.delete()
        print("<COMPUTER> COMPUTER DELETED")



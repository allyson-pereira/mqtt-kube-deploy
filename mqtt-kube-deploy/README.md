# MQTT Docker and Kubernetes Example
This example project uses the following image: https://hub.docker.com/_/eclipse-mosquitto

The goal is to explain how to deploy this image in Docker and Kubernetes.

## Mosquitto
Mosquitto should be installed and config should allow exernal listeners.
```
allow_anonymous true
listener 1883 0.0.0.0
```
## Docker
Docker should be pre-installed on Linux machines. Run the following command to confirm that Docker is installed and working correctly:
```
docker run hello-world
```
If Docker is not installed, the output will show the command needed to install Docker.
## Kubernetes
Microk8s should be installed. The following add-ons should also be enabled:
```
microk8s enable dns
microk8s enable community
microk8s enable keda
microk8s enable ha-cluster
microk8s enable host-access
microk8s enable registry
```
Microk8s also must have a valid configuration in order to function. If you are reinstalling microk8s, please check the configuration with the following command:
```
microk8s status
```
This should return an output confirming microk8s is running, and a display of the enabled and disabled add-ons. If microk8s is not running, confirm microk8s config with the following command:
```
microk8s config
```
If any listed output is null, uninstall and reinstall microk8s and check again. If not, run the following commands on Linux to create the new, valid microk8s config file:
```
microk8s config > ~/.kube/config 
sudo usermod -a -G microk8s $USER 
sudo chown -f -R $USER ~/.kube
su - $USER
```
### Setup
#### Linux
```
sudo snap install microk8s --classic
sudo apt-get install iptables-persistent
sudo iptables -P FORWARD ACCEPT
sudo usermod -a -G microk8s $USER 
su - $USER 
sudo apt install mosquitto
echo "allow_anonymous true" | sudo tee /etc/mosquitto/conf.d/custom.conf
echo "listener 1883 0.0.0.0" | sudo tee -a /etc/mosquitto/conf.d/custom.conf

sudo systemctl restart mosquitto
sudo systemctl status mosquitto
```
#### Windows
1. Install microk8s https://microk8s.io/docs/install-windows
2. Install docker https://docs.docker.com/desktop/install/windows-install/
3. Install mosquitto https://mosquitto.org/download/

## Deployment
Two pods and two images are needed for this - one for the broker, and one for the database. The broker image must be pulled from the Docker repository, and the other can be built with the included Dockerfile. Once this is done, both images must be tagged and pushed through to the private repository, where they can then be pulled and run by Kubernetes.

This must first be done fully with the broker pod. After the broker pod is finished and running, the IP address of the broker may be obtained and implimented into all code that needs it.
```
docker pull eclipse-mosquitto:latest
docker tag eclipse-mosquitto:latest localhost:32000/eclipse-mosquitto:registry
docker push localhost:32000/eclipse-mosquitto:registry

microk8s kubectl apply -f brokerdep.yaml
```

Kubernetes will pull the image from the repository, bind ports, and add appropriate Listener settings to the config file, as configured by the yaml file.

After this is complete, wait a few minutes for the pod to deploy before getting the broker IP address from an output wide request:

```
microk8s kubectl get pods -owide
```
Supply any code that needs to contact the broker with this IP address prior to constructing your images.

Once this is done, the image and pods may be constructed:
```
docker build -t pcdbtest:latest .
docker tag pcdbtest:latest localhost:32000/pcdbtest:registry
docker push localhost:32000/pcdbtest:registry

microk8s apply -f pcdbpod.yaml
```
The results may be checked by get pods or deployments, and pod logs may be retrieved to confirm output:
```
microk8s kubectl get pods -owide
microk8s kubectl get deployments -owide
microk8s kubectl get logs [PODNAME]
```
For more troubleshooting information, please see commands.txt.
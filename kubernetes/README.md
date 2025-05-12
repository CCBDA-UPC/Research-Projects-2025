# Research topic - AWS EKS as an alternative to AWS Elastic Beanstalk

## Kubernetes

Kubernetes is an open sourced orchestration tool developed by Google to manage containers over several machines, or nodes. While Docker loads and runs containers, Kubernetes orchestrates and manages them. With Kubernetes you can run and manage a very large amount of containers efficiently.

<img src="../img/Kubernetes_comp.jpg" width=70% height=70%>

Here are some of the main components of kubernetes:

- **Pod:** The smallest element in Kubernetes. It contains one or more containers that have the same network and storage
- **Node:** A machine which the pods run on
- **Cluster:** A cluster is a set of nodes which is managed by the Kubernetes control plane
- **Kubernetes Control Plane:** Is built of several components for handling the Cluster. It makes sure the desired state matches the current state.

Say for example, you always want to run 3 containers. Using Kubernetes, these containers can be self healing,if one fails it will automatically be replaced. Kubernetes handles scaling; if the demand increases, it can add more containers automatically. Load balancing is used to distribute the traffic evenly across these pods. By using rolling updates new versions are deployed quickly.

## Amazon Elastic Kubernetes Service (EKS)

What is EKS
Amazon Elastic Kubernetes Service (EKS) is a managed Kubernetes service run by Amazon Web Services (AWS). It lets you run Kubernetes on AWS without having to set up or manage the control plane yourself. Amazon EKS can do anything you can do in regular Kubernetes, but AWS takes care of the setup, maintenance and infrastructure behind the scenes.

The benefit of using Amazon EKS is that you save time and effort. With this, you do not need to spend time on the complex parts of setting up Kubernetes because AWS does it for you. So you can focus more on running and deploying your applications instead of focusing on the infrastructure.

The downside of using Amazon EKS is that it costs more than Kubernetes. AWS charges extra for managing the control plane, and it could also be a little complex to get started with if you are new to Kubernetes or AWS. Also, since Amazon EKS is tightly connected to other AWS services it may make it harder to switch to another provider later.

## Amazon EKS Architecture

**EKS Standard:** EKS manage the Kubernetes Control Plane. You have to setup and manage the EC2 instances yourself
EKS Auto (Fargate): With EKS Auto Nodes are managed as well, and EC2 instances are managed for you

<img src="../img/AWS_EKS_auto_vs_standard.JPG" width=70% height=70%>

## Amazon EKS vs AWS Elastic Beanstalk

AWS Elastic Beanstalk is a Platform-as-a-Service (PaaS) and is designed to be easy to use by just uploading your code and then AWS handles everything else like servers, deploying the app, load balancing, scaling, and monitoring. On the other side, Amazon EKS is a more powerful and flexible tool, but also more complex than Elastic Beanstalk, and you can use it when you want full control over how your containers run, scale, and interact with each other.

||Amazon EKS| AWS Elastic Beanstalk|
| --- | --- | --- |
|Ease of use | More complex, and requires Kubernetes knowledge.| Easy to get started for developers who do not want to manage infrastructure. Minimal setup. |
|Use case| Scalable systems, microservices, containers.| Simple web apps, REST APIs|
|Scaling| Highly customizable and powerful.| Automatic but basic.|
|Control|Full control over infrastructure and how apps are deployed and run.| Limited control over the underlying infrastructure (AWS handles almost everything).|
|Technology|Runs containerized apps with Kubernetes| Works with EC2/ELB, no containers required.|

## In which cases would you use EKS

If your team chose to use EKS you should already be familiar with Kubernetes, since it is required to use EKS. The team is maybe a part of a medium to larger business, and want more control, flexibility, and customization of their infrastructure. For example a DevOps oriented workflow can be a good fit for EKS. A startup working on an MVP, would instead opt to use something like Elastic Beanstalk, so they can focus more on the code and less on how the resources are handled.

## Our experience with EKS

We tried to setup EKS for the Django applications used in the labs

EKS cluster created

<img src="../img/EKS_cluster_created.png" width=70% height=70%>

#### Configure laptop to communicate with the cluster
Create a kubeconfig file for our cluster

```console
% aws eks update-kubeconfig --region us-east-1 --name interesting-bluegrass-dinosaur                       
Added new context arn:aws:eks:us-east-1:675835039352:cluster/interesting-bluegrass-dinosaur to /Users/User/.kube/config
```
Test configuration

```console
% kubectl get svc
NAME         TYPE        CLUSTER-IP   EXTERNAL-IP   PORT(S)   AGE
kubernetes   ClusterIP   10.100.0.1   <none>        443/TCP   17m
```

#### Create Nodes

Nodegroup `research-nodegroup-1` added with two Nodes, but the status of two nodes are `NotReady`

```console
% kubectl get nodes                                  
NAME                            STATUS     ROLES    AGE   VERSION
ip-172-31-13-219.ec2.internal   NotReady   <none>   27m   v1.32.3-eks-473151a
ip-172-31-20-251.ec2.internal   NotReady   <none>   27m   v1.32.3-eks-473151a
```
By checking kubelet log we found the following error
```console
% journalctl -xeu kubelet
May 05 12:58:27 ip-172-31-95-47.ec2.internal kubelet[1624]: E0505 12:58:27.330578    1624 kubelet.go:3011] "Container runtime network not ready" networkReady="NetworkReady=false reason:NetworkPluginNotReady message:Network plugin returns error: cni plugin not initialized"
```
And then we found `CoreDNS`, `Kube-proxy`, `VPC CNI` networking plugins are not configured.

Network plugins added.

<img src="../img/network_plugins_added.png" width=70% height=70%>

The status of nodes have changed to `Ready`.

We can see all the running pods.

```console
% kubectl get pods --all-namespaces  
NAMESPACE     NAME                              READY   STATUS    RESTARTS   AGE
kube-system   aws-node-g8n94                    2/2     Running   0          22m
kube-system   aws-node-r657h                    2/2     Running   0          22m
kube-system   coredns-6b9575c64c-c6fxw          1/1     Running   0          22m
kube-system   coredns-6b9575c64c-t5ssk          1/1     Running   0          22m
kube-system   kube-proxy-97rq8                  1/1     Running   0          22m
kube-system   kube-proxy-mltpw                  1/1     Running   0          22m
kube-system   metrics-server-754d6bd6b7-459ch   0/1     Pending   0          4h42m
kube-system   metrics-server-754d6bd6b7-xjx4f   0/1     Pending   0          4h42m
```
#### Deploy application

Create namespace
```console
% kubectl create namespace ccbda          
namespace/ccbda created
```

Create a Kubernetes deployment

`ccbda-web-app.yaml`
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ccbda-web-app
  namespace: ccbda
  labels:
    app: ccbda-web-app
spec:
  replicas: 2
  selector:
    matchLabels:
      app: ccbda-web-app
  template:
    metadata:
      labels:
        app: ccbda-web-app
    spec:
      containers:
      - name: django-web-app
        image: 675835039352.dkr.ecr.us-east-1.amazonaws.com/django-webapp-docker-repo:v1.2.0
        ports:
        - name: http
          containerPort: 8000
        imagePullPolicy: IfNotPresent
        env:
        - name: DJANGO_DEBUG
          value: "False"
        - name: DJANGO_ALLOWED_HOSTS
          value: "localhost:127.0.0.1:0.0.0.0:172.*.*.*"
        - name: DJANGO_SECRET_KEY
          value: "-lm+)b44uap8!0-^1w9&2zokys(47)8u698=dy0mb&6@4ee-hh"
        - name: DJANGO_LOGLEVEL
          value: "info"
        - name: CCBDA_SIGNUP_TABLE
          value: "ccbda-signup-table"
      nodeSelector:
        kubernetes.io/os: linux
```

```console
% kubectl apply -f ccbda-web-app.yaml
deployment.apps/ccbda-web-app created
```

Pods are running.
```console
% kubectl get pods -n ccbda
NAME                            READY   STATUS    RESTARTS   AGE
ccbda-web-app-cc5b5877f-f8zzc   1/1     Running   0          90s
ccbda-web-app-cc5b5877f-nxtf8   1/1     Running   0          81s
```


Create a Kubernetes service
```yaml
apiVersion: v1
kind: Service
metadata:
  name: ccbda-web-service
  namespace: ccbda
  labels:
    app: ccbda-web-app
spec:
  selector:
    app: ccbda-web-app
  ports:
    - protocol: TCP
      port: 8000
      targetPort: 8000
```

```console
% kubectl apply -f ccbda-web-service.yaml 
service/ccbda-web-service created
```
Django web application ClusterIp

```console
% kubectl get service  -n ccbda
NAME                TYPE        CLUSTER-IP      EXTERNAL-IP   PORT(S)    AGE
ccbda-web-service   ClusterIP   10.100.37.151   <none>        8000/TCP   69m
```
Due to the limitations of the Learner Lab role, we cannot deploy the AWS Load Balancer Controller to expose the web to the internet. We can only access the web page on the nodes within the EKS cluster.

```shell
lynx http://10.100.37.151:8000
```

<img src="../img/lynx_ccbda-web.png" width=70% height=70%>

#### Some screenshots of the cluster

Cluster view

<img src="../img/eks-cluster-view.png" width=70% height=70%>

`ccbda` nodegroup with 2 nodes

<img src="../img/eks-node-group.png" width=70% height=70%>

`ccbda-web-app` deployment with 2 pods

<img src="../img/eks-ccbda-deployment.png" width=70% height=70%>

`ccbda-web-app` service to create a ClusterIP

<img src="../img/eks-service.png" width=70% height=70%>





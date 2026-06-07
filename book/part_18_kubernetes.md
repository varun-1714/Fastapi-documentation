# Part 18: Kubernetes Orchestration

---

## Chapter 1: Deploying FastAPI on Kubernetes (Pods, Deployments, Ingress & HPA)

### 1. Introduction
While Docker containers package applications, managing them at scale across multiple servers requires an orchestration engine. Kubernetes (K8s) is the industry standard for managing containerized workloads, handling deployments, routing, scaling, and self-healing.

### 2. Concept Explanation
* **Pod**: The smallest deployable unit in Kubernetes, hosting one or more tightly coupled containers.
* **Deployment**: Declares the desired state of pods (e.g. running 3 replicas) and handles rollouts and updates.
* **Service**: Exposes a set of Pods as a network service with a stable IP address and load balancer.
* **Ingress**: Manages external HTTP/S access to services, handling routing rules, SSL termination, and hostnames.
* **Horizontal Pod Autoscaler (HPA)**: Automatically scales the number of active pods up or down based on CPU or memory usage.

### 3. Architecture Explanation
The Kubernetes architecture routes incoming client requests through an Ingress controller to a Service load balancer, which distributes traffic to active Pod replicas.
```
Client Request ---> [ Ingress Controller ] ---> [ Service Load Balancer ] ---> [ Pod Replica 1 / 2 / 3 ]
                                                                                      ^
                                                                          [ Auto Scaled by HPA ]
```

### 4. Visual Workflow
```
CPU > 70% ---> HPA detects spike ---> Spawns new Pods ---> Service updates routing tables
```

### 5. Real-World Scenario
An enterprise API needs to run on a Kubernetes cluster. The service must scale automatically between 2 and 10 replicas based on CPU load, expose health probes to the cluster, and route external traffic to the pods.

### 6. Step-by-Step Implementation
1. Write a Kubernetes deployment manifest containing ConfigMaps, Deployments, Services, Ingress rules, and HPA configurations.
2. Deploy the manifests to a K8s cluster (e.g. Minikube or EKS).

### 7. Source Code Examples
#### Production-Ready Kubernetes manifest (`deployment.yaml`)
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: fastapi-config
data:
  DATABASE_URL: "postgresql+asyncpg://admin:password@postgres-service:5432/db"
  REDIS_URL: "redis://redis-service:6379/0"
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: fastapi-deployment
  labels:
    app: fastapi-app
spec:
  replicas: 3
  selector:
    matchLabels:
      app: fastapi-app
  template:
    metadata:
      labels:
        app: fastapi-app
    spec:
      containers:
      - name: fastapi-container
        image: myregistry.azurecr.io/fastapi-app:1.0.0
        ports:
        - containerPort: 8000
        envFrom:
        - configMapRef:
            name: fastapi-config
        resources:
          limits:
            cpu: "500m"
            memory: "512Mi"
          requests:
            cpu: "250m"
            memory: "256Mi"
        livenessProbe:
          httpGet:
            path: /healthz
            port: 8000
          initialDelaySeconds: 15
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /readyz
            port: 8000
          initialDelaySeconds: 20
          periodSeconds: 10
---
apiVersion: v1
kind: Service
metadata:
  name: fastapi-service
spec:
  selector:
    app: fastapi-app
  ports:
    - protocol: TCP
      port: 80
      targetPort: 8000
  type: ClusterIP
---
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: fastapi-ingress
  annotations:
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
spec:
  ingressClassName: nginx
  rules:
  - host: api.corp.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: fastapi-service
            port:
              number: 80
---
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: fastapi-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: fastapi-deployment
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
```

### 8. CLI Deploying Examples
Apply manifests to the cluster:
```bash
kubectl apply -f deployment.yaml
```
Verify running resources:
```bash
kubectl get deployments,services,pods,hpa
# Output:
# NAME                                 READY   UP-TO-DATE   AVAILABLE   AGE
# deployment.apps/fastapi-deployment   3/3     3            3           1m
#
# NAME                      TYPE        CLUSTER-IP   EXTERNAL-IP   PORT(S)   AGE
# service/fastapi-service   ClusterIP   10.96.0.1    <none>        80/TCP    1m
```

### 9. Common Mistakes
Failing to specify resource limits and requests in container definitions, which can cause pods to consume all host memory and crash other workloads on the node.

### 10. Best Practices
Always set explicit resource configurations (`limits` and `requests`) on containers. Configure liveness and readiness probes to check container health, and deploy applications using Horizontal Pod Autoscalers to handle traffic spikes.

### 11. Interview Questions
* **Q: What is the difference between resource `requests` and `limits` in a Kubernetes pod?**
  * *A*: `requests` is the minimum amount of CPU and memory Kubernetes guarantees to allocate to the pod. `limits` is the maximum amount of resources the pod is allowed to consume; if it exceeds memory limits, it is terminated with an Out Of Memory (OOM) error.

### 12. Chapter Summary
Kubernetes orchestrates container workloads at scale. Services load balance internal traffic, Ingress handles routing, and HPAs scale pods based on resource usage.

### 13. Practice Exercises
Add a readiness probe config that sets a timeout of 5 seconds and requires 2 successful checks before marked healthy.

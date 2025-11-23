
#!/bin/bash

# Define Namespace (Based on your previous logs)
NAMESPACE="django-app"

echo "======================================================="
echo "🚀 XAV_TECHNOLOGY: LOCAL CI/CD & HEALTH CHECK PIPELINE"
echo "======================================================="

# --- STEP 1: INFRASTRUCTURE HEALTH CHECK ---
echo "🔍 1. Checking Infrastructure Health..."

# Check if Helm Release exists
if helm list -n $NAMESPACE | grep -q "monitoring"; then
    echo "✅ Helm Chart 'monitoring' is installed."
else
    echo "❌ CRITICAL: Monitoring stack not found! Installing now..."
    helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
    helm install monitoring prometheus-community/kube-prometheus-stack -n $NAMESPACE --create-namespace
fi

# Check if Prometheus Pods are actually READY
echo "🏥 Checking Prometheus Pod Status..."
# This command waits until the pods are actually running
kubectl wait --for=condition=ready pod -l "app.kubernetes.io/instance=monitoring" -n $NAMESPACE --timeout=120s

if [ $? -eq 0 ]; then
    echo "✅ Observability Stack is HEALTHY."
else
    echo "❌ Error: Prometheus pods are not starting. Check logs."
    exit 1
fi

# --- STEP 2: DEPLOY APPLICATION ---
echo "💾 2. Deploying Application Layers..."
kubectl apply -f k8s/config-secrets.yaml
kubectl apply -f k8s/mysql.yaml
kubectl apply -f k8s/django.yaml

# Force update to pull new image
kubectl rollout restart deployment/django-deployment

# --- STEP 3: LOAD TESTING ---
echo "🧪 3. Running k6 Load Test..."
kubectl delete job xav-load-tester --ignore-not-found
kubectl apply -f k6-load-test.yaml
echo "⏳ Waiting for test to complete..."
kubectl wait --for=condition=complete job/xav-load-tester --timeout=150s

# --- STEP 4: AUTOMATED PORT FORWARDING ---
echo "📊 4. Setting up Grafana Access..."

# Get the Grafana Pod Name dynamically
GRAFANA_POD=$(kubectl get pod -n $NAMESPACE -l "app.kubernetes.io/name=grafana" -o jsonpath="{.items[0].metadata.name}")

echo "🔓 Grafana Pod found: $GRAFANA_POD"
echo "🔑 Admin Password (Decoded):"
kubectl get secret --namespace $NAMESPACE monitoring-grafana -o jsonpath="{.data.admin-password}" | base64 -d ; echo

echo "🌐 Port Forwarding started in background..."
echo "👉 Open http://localhost:3000 in your browser"

# Run port-forward in the background &
kubectl port-forward $GRAFANA_POD 3000:3000 -n $NAMESPACE &
PID=$!

echo "⚠️  Press CTRL+C to stop the Port Forwarding and exit."
wait $PID

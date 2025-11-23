#!/bin/bash

NAMESPACE="django-app"

echo "======================================================="
echo "🧹 XAV_TECHNOLOGY: CLEANUP & SHUTDOWN"
echo "======================================================="

# 1. Stop the Load Test (Immediate CPU relief)
echo "🛑 1. Stopping k6 Load Test..."
kubectl delete job xav-load-tester --ignore-not-found

# 2. Stop Port Forwarding (Frees up port 3000)
echo "🔌 2. Killing background Port-Forwarding..."
# This finds any 'kubectl port-forward' process and kills it
pkill -f "kubectl port-forward" || echo "No port-forwarding found."

# 3. Delete the Application (Django & MySQL)
echo "🗑️  3. Deleting Django & MySQL..."
kubectl delete -f k8s/django.yaml --ignore-not-found
kubectl delete -f k8s/mysql.yaml --ignore-not-found
kubectl delete -f k8s/config-secrets.yaml --ignore-not-found

# 4. Remove Monitoring Stack (Frees up the most RAM)
echo "📉 4. Uninstalling Prometheus & Grafana..."
helm uninstall monitoring -n $NAMESPACE --ignore-not-found

echo "======================================================="
echo "✅ CLEANUP COMPLETE. Your apps are stopped."
echo "======================================================="
echo "💡 NOTE: The Kind Cluster is still running (but empty)."
echo "   To delete the cluster entirely and free ALL memory, run:"
echo "   kind delete cluster --name xav-tech-cluster"
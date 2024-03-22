# Cloud Advanced 2024 - Exercise 1 (Nextcloud @ Kubernetes)

This setup is meant to establish a Kubernetes cluster of machines, running and exposing access to Nextcloud.

It is mainly based on the Nextcloud helm chart, made available [here](https://nextcloud.github.io/helm/). Additional `yml` manifests have been crafted for allowing proper use of all needed components, as well as to customize the installation.

## Namespace

All resources allocated within the scope of this setup belong to a previously created **namespace** called `nextcloud`. In order to create such namespace, run

```bash
$ kubectl create namespace nextcloud
```

## Files

### `nextcloud_pvc.yml` and `postgres_pvc.yml`

These files serve as Persistent Storage Volumes Claims. They are needed to reserve storage resources that allow for pod persistence across deploys. This is a wanted behavior in this kind of system, which is meant to persist files, users and settings across deploys and restarts in general, including when one or more pods crash.

```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: postgresql-pvc
  namespace: nextcloud
spec:
  accessModes:
    - ReadWriteOnce
  storageClassName: local-path
  resources:
    requests:
      storage: 8Gi
```

In this setup and for the sake of having a working Proof of Concept, both claimed volumes (one for the PostgreSQL database persistence, the other for all files belonging to the Nextcloud installation) are sized at 8GiB and reside locally. The claims are contained in the two aforementioned YAML files, and can be applied with

```bash
$ kubectl -n nextcloud apply -f nextcloud_pvc.yml 
$ kubectl -n nextcloud apply -f postgres_pvc.yml
```

### `secrets.yml`

The secrets file contains all credentials needed to configure Nextcloud and PostgreSQL with administrator and regular users. In a real world scenario such credentials would of course be _kept secret_ and loaded at runtime from files or environment variables. The secrets file has to be loaded with

```bash
$ kubectl -n nextcloud apply -f secrets.yml
```

## Deployment

Once the necessary files are loaded and the cluster is setup with at least one worker node and enough storage to accomodate the claimed resources, the `nextcloud/nextcloud` Helm chart can be pulled and installed injecting the custom values specified in `values.yml` (configurations are summarized in the report).

```bash
$ helm install nextcloud nextcloud/nextcloud --namespace nextcloud --values values.yaml 
```
# Cloud Advanced 2024 - Exercise 2 (MPI @ Kubernetes)

This setup is meant to perform a set of MPI benchmark tests aimed at measuring performance of communication and collective operations run within two pods in a Kubernetes cluster.

The benchmark suite of choice is the OSU MPI benchmarks and the selected tests are latency and broadcast collective operation. The MPI implementation used for this setup is OpenMPI.

## Setup

In order to be able to spawn MPI processes on Kubernetes pods, the [MPI operator](https://github.com/kubeflow/mpi-operator) has been used. Using the MPI operator for performing two-process benchmarks requires a total of three agents: a launcher node and two worker nodes. Job dispatching is done creating a Docker image to be built and deployed to all involved nodes. Such Docker image installs all needed software to run the tests and compiles the tests code from its source.

In order to have such code available locally to be copied into the image, download it and unpack it in the same folder where the `Dockerfile` is.

```bash
$ wget http://mvapich.cse.ohio-state.edu/download/mvapich/osu-micro-benchmarks-7.3.tar.gz
$ tar xvf osu-micro-benchmarks-7.3.tar.gz
$ mv osu-micro-benchmarks-7.3.tar.gz osu-7.3 # needed for the image build to work
$ rm osu-micro-benchmarks-7.3.tar.gz
```

Before building the image, a local image registry has to be setup on every node. It is not possible to create a single registry on the local network, as Docker will try to connect to any registry using HTTPS and demanding a valid certificate for such connection. According to the [Docker documentation](https://docs.docker.com/reference/cli/dockerd/#insecure-registries), it should be possible to configure custom insecure registries, but no luck was had with this method during testing of this implementation.

The following command can be used to setup an image registry on `localhost:5000`:

```bash
$ docker run -d -p 5000:5000 --restart=always --name registry registry:2
```

Then, the required Docker image can be built and pushed to the local registry using

```bash
$ docker build -t localhost:5000/mpi-osu .
$ docker push localhost:5000/mpi-osu
```

After these steps are successfully carried out, all nodes are ready to execute MPI tests.

## Execution

Single-node and multi-node tests can be performed applying either the `osu-single-node.yaml` or the `osu-multi-nodes.yaml` file. Tests can be dispatched using

```bash
$ kubectl create -f <selected yaml file>
```

and canceled/terminated using

```bash
$ kubectl delete -f <selected yaml file>
```

With the results being printed on the stdout of the launcher nodes, it is possible to collect them using

```bash
$ kubectl logs -f <launcher pod name>
```

It is possible to retrieve the name of the launcher pod by running

```bash
$ kubectl get pods
```

and looking for a pod named `osu-launcher-*`.

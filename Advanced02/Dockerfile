FROM mpioperator/openmpi-builder:latest as builder

COPY osu-7.3 /src/osu-7.3
RUN echo $(which mpicc)
RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get -yq install file apt-utils build-essential -y
RUN cd /src/osu-7.3/ && ./configure CC=$(which mpicc) CXX=$(which mpicxx) --disable-dependency-tracking && make

FROM mpioperator/openmpi:latest

COPY --from=builder /src/osu-7.3 /home/mpiuser/osu-7.3
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
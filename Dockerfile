FROM ubuntu
# https://github.com/david4096/mapd-core#dependencies
RUN apt-get update  --fix-missing
RUN apt-get upgrade --yes
RUN apt install -y \
    build-essential \
    cmake \
    cmake-curses-gui \
    git \
    clang \
    clang-format \
    llvm \
    llvm-dev \
    libboost-all-dev \
    libgoogle-glog-dev \
    golang \
    libssl-dev \
    libevent-dev \
    default-jre \
    default-jre-headless \
    default-jdk \
    default-jdk-headless \
    maven \
    libncurses5-dev \
    binutils-dev \
    google-perftools \
    libdouble-conversion-dev \
    libevent-dev \
    libgdal-dev \
    libgflags-dev \
    libgoogle-perftools-dev \
    libiberty-dev \
    libjemalloc-dev \
    liblz4-dev \
    liblzma-dev \
    libsnappy-dev \
    zlib1g-dev \
    autoconf \
    autoconf-archive \
    wget

WORKDIR /build

RUN apt build-dep -y thrift-compiler
ARG THRIFT_VERSION=0.10.0
RUN wget http://apache.claz.org/thrift/$THRIFT_VERSION/thrift-$THRIFT_VERSION.tar.gz
RUN tar xvf thrift-$THRIFT_VERSION.tar.gz
WORKDIR /build/thrift-$THRIFT_VERSION
RUN ./configure \
    --with-lua=no \
    --with-python=no \
    --with-php=no \
    --with-ruby=no \
    --prefix=/usr/local/mapd-deps
RUN make -j $(nproc)
RUN make install

WORKDIR /build

ARG BLOSC_VERSION=1.11.3
RUN wget --continue https://github.com/Blosc/c-blosc/archive/v$BLOSC_VERSION.tar.gz
RUN tar xvf v$BLOSC_VERSION.tar.gz
ARG BDIR="c-blosc-$BLOSC_VERSION/build"
RUN rm -rf "$BDIR"
RUN mkdir -p "$BDIR"
WORKDIR /build/$BDIR
RUN cmake \
    -DCMAKE_BUILD_TYPE=Release \
    -DCMAKE_INSTALL_PREFIX=/usr/local/mapd-deps \
    -DBUILD_BENCHMARKS=off \
    -DBUILD_TESTS=off \
    -DPREFER_EXTERNAL_SNAPPY=off \
    -DPREFER_EXTERNAL_ZLIB=off \
    -DPREFER_EXTERNAL_ZSTD=off \
    ..
RUN make -j $(nproc)
RUN make install

WORKDIR /build

ARG FOLLY_VERSION=2017.04.10.00
RUN wget --continue https://github.com/facebook/folly/archive/v$FOLLY_VERSION.tar.gz
RUN tar xvf v$FOLLY_VERSION.tar.gz
WORKDIR /build/folly-$FOLLY_VERSION/folly
RUN /usr/bin/autoreconf -ivf
RUN ./configure --prefix=/usr/local/mapd-deps
RUN make -j $(nproc)
RUN make install

WORKDIR /build

ARG BISON_VERSION=1.21-45
RUN wget --continue https://github.com/jarro2783/bisonpp/archive/$BISON_VERSION.tar.gz
RUN tar xvf $BISON_VERSION.tar.gz
WORKDIR /build/bisonpp-$BISON_VERSION
RUN ./configure
RUN make -j $(nproc)
RUN make install

WORKDIR /build

ENV LD_LIBRARY_PATH=/usr/local/cuda/lib64:$LD_LIBRARY_PATH
ENV LD_LIBRARY_PATH=/usr/lib/jvm/default-java/jre/lib/amd64/server:$LD_LIBRARY_PATH
ENV LD_LIBRARY_PATH=/usr/local/mapd-deps/lib:$LD_LIBRARY_PATH
ENV LD_LIBRARY_PATH=/usr/local/mapd-deps/lib64:$LD_LIBRARY_PATH

ENV PATH=/usr/local/cuda/bin:$PATH
ENV PATH=/usr/local/mapd-deps/bin:$PATH

RUN export LD_LIBRARY_PATH PATH

# latest master commit hash 6-5-2017
RUN git clone https://github.com/david4096/mapd-core.git
WORKDIR /build/mapd-core
RUN git checkout b6d6cc332ae1b53ccb6ab7f70d7a09ce33ce6ee0
RUN mkdir target
WORKDIR /build/mapd-core/target
# TODO make into arguments
RUN cmake -DCMAKE_BUILD_TYPE=debug -DENABLE_CUDA=off ..
RUN make -j 4

EXPOSE 9092

CMD /build/mapd-core/startmapd --non-interactive --data /mapd-storage/data --config /mapd-storage/mapd.conf

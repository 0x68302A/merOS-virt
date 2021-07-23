#/!bin/bash

export BUILD_PATH=$MOS_PATH/etc/build/pkg

build_static_tor() {

	export TOR_STATIC=$BUILD_PATH/tor_static

	mkdir -p $TOR_STATIC
	cd $TOR_STATIC

	## Build zlib
	git clone https://github.com/madler/zlib.git --depth 1
	cd zlib
	./configure --prefix=$PWD/install
	make -j$(nproc)
	make install

	cd $TOR_STATIC

	## Build libevent
	git clone https://github.com/libevent/libevent.git --depth 1
	cd libevent
	./autogen.sh
	./configure --prefix=$PWD/install \
           --disable-shared \
           --enable-static \
           --with-pic
	make -j$(nproc)
	make install

	cd $TOR_STATIC

	## Build openssl
	git clone https://github.com/openssl/openssl.git --depth 1
	cd openssl
	./config --prefix=$PWD/install no-shared no-dso
	make -j$(nproc)
	make install

	cd $TOR_STATIC

	git clone https://gitlab.torproject.org/tpo/core/tor.git --depth 1
	cd tor
	./autogen.sh
	./configure --prefix=$PWD/install \
            --enable-static-tor \
            --with-libevent-dir=$PWD/../libevent-2.1.8-stable/install \
            --with-openssl-dir=$PWD/../openssl/install \
            --with-zlib-dir=$PWD/../zlib-1.2.11/install \
	    --disable-asciidoc
	make -j$(nproc)
	make install

}

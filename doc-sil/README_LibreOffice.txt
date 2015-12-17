

The installer is in:
  workdir/installation/LibreOfficeDev/msi/install/en-US/LibreOfficeDev_5.1.0.0.beta2_Win_x86.msi

Autogen config for build on Windows 7:

/cygdrive/d/sources/libo/src/autogen.sh \
    --without-junit \
	--without-helppack-integration \
	--enable-extension-integration \
	--disable-gtk \
	--enable-scripting-beanshell \
	--enable-scripting-javascript \
	--enable-ext-wiki-publisher \
	--enable-ext-nlpsolver \
	--enable-online-update \
	--with-help \
	--with-myspell-dicts \
	--with-package-format=msi \
	--enable-mergelibs \
	--with-vendor="SIL International" \
	--with-build-version="5.1.0.0.beta2-khmer.1" \
	--disable-dependency-tracking \
    --with-junit=/cygdrive/d/sources/junit-4.10.jar \
    --with-ant-home=/cygdrive/d/sources/apache-ant-1.9.6 \
	--with-parallelism=4 \
	--srcdir=/cygdrive/d/sources/libo/src \
	--enable-option-checking=fatal \
	
Note that --disable-dependency-tracking isn't required, but it speeds up the build, and dependency-tracking on windows seems unreliable at best.
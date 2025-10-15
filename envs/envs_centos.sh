#!/bin/bash

if [ "$EUID" -ne 0 ]; then 
    echo "please run this script with root"
    exit 1
fi

check_package() {
    rpm -q "$1" &> /dev/null
}

echo "installing system dependencies..."

if ! yum grouplist "Development Tools" installed &> /dev/null; then
    echo "Installing Development Tools..."
    yum groupinstall -y "Development Tools"
else
    echo "Development Tools already installed"
fi

PACKAGES=(
    "xorg-x11-server-Xvfb"
    "xorg-x11-xauth"
    "gnome-screenshot"
    "xclip"
    "libjpeg-devel"
    "libpng-devel"
    "freetype-devel"
    "zlib-devel"
    "nss"
    "cups-libs"
    "libXScrnSaver"
    "libXrandr"
    "libXcomposite"
    "libXcursor"
    "libXdamage"
    "libXi"
    "libXtst"
    "libXrender"
    "libXt"
    "libX11-xcb"
    "libxcb"
    "libdrm"
    "mesa-libgbm"
    "alsa-lib"
    "pango"
    "cairo"
    "at-spi2-atk"
    "gtk3"
    "gdk-pixbuf2"
    "lsof"
    # for font
    "google-noto-sans-sinhala-fonts"  
    "google-noto-sans-fonts"          
    "google-noto-serif-fonts"         
    "google-noto-sans-cjk-fonts"      
    "dejavu-sans-fonts"              
    "dejavu-serif-fonts"              
    "dejavu-sans-mono-fonts"          
    "liberation-fonts"                
    "fontconfig"                      
    "fontconfig-devel"                
    "google-noto-emoji-fonts"       
    "google-noto-color-emoji-fonts"
)

PACKAGES_TO_INSTALL=()
for package in "${PACKAGES[@]}"; do
    if ! check_package "$package"; then
        echo "Package $package needs to be installed"
        PACKAGES_TO_INSTALL+=("$package")
    else
        echo "Package $package is already installed"
    fi
done

if [ ${#PACKAGES_TO_INSTALL[@]} -gt 0 ]; then
    echo "Installing missing packages..."
    yum install -y "${PACKAGES_TO_INSTALL[@]}"
else
    echo "All required packages are already installed"
fi
The name leet stands for "Linux exquisite encryption tool", it will be a software application for on-the-fly encryption, similar in its functionality to TrueCrypt.

The goal of leet however is to be simpler and as user friendly as possible, making encryption and securing of information accessible to anybody, even those who don't necessarily have any prior knowledge of data securing, algorithms and encryption. However it's not targeted at this group of users only, part of the ambition of this project is to reach companies, institutions, governments (etc...) as well.

For a more complete description of the leet project, it has been decided to link the Sourceforge pages describing the software application as well as the encryption algorithm to be used.

Here: https://sourceforge.net/p/home-of-leet/wiki/browse_pages/

## Build instructions
Use: python setup.py build

PS: To successfully compile your own copy of leet you need to install "python3-pip" then with pip you need to install "cx_freeze" via "sudo pip3 install cx_freeze" command (considering you are using a ubuntu/debian based distro). You might also need to run the following command "sudo apt install zlib1g-dev" to install "lz", and "sudo apt install python3-numpy" then you can finally run "python3 setup.py build" in the extracted directory to build the "driver" which you will then execute.

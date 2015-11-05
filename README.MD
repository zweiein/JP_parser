Required
----
* CRF++-0.58
* mecab-0.996
* cabocha-0.69
* mecab-ipadic-2.7.0-20070801


`tar zxvf CRF++-0.58.tar.gz`   
`cd CRF++-0.58/`   
`./configure`   
`make`   
`sudo make install`   
sudo ldconfig   
cd ..   
bzip2 -dc cabocha-0.68.tar.bz2 | tar xvf -   
bzip2 -dc cabocha-0.68.tar.bz2   
cd cabocha-0.69/   
make check   
sudo make install   
ls   
make check   
./configure   
make   

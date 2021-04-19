# Verify using Peregrine

`cd Peregrine`

`source tbb2020/bin/tbbvars.sh intel64`

`make count -j CC=g++-10`

`bin/count <path to tesseract-python>/peregine_dataset/gnp_network_1000/ <path to tesseract-python>/peregine_dataset/test_patterns/test_pattern_1.txt 16`
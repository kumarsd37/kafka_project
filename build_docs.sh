#!/usr/bin/env bash

cur_dir=$(dirname $0)

output_dir='docs'

# to get the module level rst, we use - sphinx-apidoc -o <output_folder> <input_folder>
# sphinx will generate modules.rst in output directory. Rename it as index.rst
sphinx-apidoc -o root_docs/rst/ /code/kafka_project/framework


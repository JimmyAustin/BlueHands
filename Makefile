test:
	py.test --pdb

testonly:
	py.test --pdb -k "__only"

build:
	solc --bin-runtime -o ./contracts/build/ ./contracts/src/branch_identifier.sol --overwrite
	solc --bin -o ./contracts/build/ ./contracts/src/branch_identifier.sol --overwrite
	solc --opcodes-runtime -o ./contracts/build/ ./contracts/src/branch_identifier.sol --overwrite
	solc --opcodes -o ./contracts/build/ ./contracts/src/branch_identifier.sol --overwrite
	solc --bin -o ./contracts/build/ ./contracts/src/hello_world.sol --overwrite
	solc --opcodes -o ./contracts/build/ ./contracts/src/hello_world.sol --overwrite
	solc --bin -o ./contracts/build/ ./contracts/src/add.sol --overwrite
	solc --opcodes -o ./contracts/build/ ./contracts/src/add.sol --overwrite

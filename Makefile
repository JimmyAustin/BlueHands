test:
	py.test

build:
	solc --bin -o ./contracts/build/ ./contracts/src/hello_world.sol --overwrite
	solc --opcodes -o ./contracts/build/ ./contracts/src/hello_world.sol --overwrite
	solc --bin -o ./contracts/build/ ./contracts/src/add.sol --overwrite
	solc --opcodes -o ./contracts/build/ ./contracts/src/add.sol --overwrite

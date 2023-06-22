import subprocess


def build_tests():
    for i in range(20):
        with open(f"Public tests/P1/In (public)/in{i // 10}{i % 10}.txt", 'r') as input_file:
            input_data = input_file.read()

        with open(f"Public tests/P1/Out (public)/out{i // 10}{i % 10}.txt", 'r') as expected_output_file:
            expected_data = expected_output_file.read()

        result = subprocess.run(['python', 'build.py'], input=input_data.encode(), capture_output=True)

        output_str = result.stdout.decode()

        # we can't just simply compare them because output from the program and expected output
        # will have different transition permutation, resulting in inequality, while language of
        # the NFA will be the same
        print(output_str, '\n', expected_data, '\n', output_str == expected_data, '\n')


def run_tests():
    for i in range(20):
        with open(f"Public tests/P2/In (public)/in{i // 10}{i % 10}.txt", 'r') as input_file:
            input_data = input_file.read()

        with open(f"Public tests/P2/Out (public)/out{i // 10}{i % 10}.txt", 'r') as expected_output_file:
            expected_data = expected_output_file.read()

        result = subprocess.run(['python', 'run.py'], input=input_data.encode(), capture_output=True)

        output_str = result.stdout.decode()

        # We can compare directly in this case, but in windows it adds \r before \n, resulting in inequality.
        # Assertion works fine in linux

        assert output_str == expected_data


if __name__ == '__main__':
    build_tests()
    run_tests()

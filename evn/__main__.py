import argparse
import evn as evn

def get_args(sysargv):
    """get command line arguments"""
    parser = argparse.ArgumentParser()
    parser.add_argument('input', type=str, nargs='+', default='')
    parser.add_argument('-f', '--filter', default='', choices=['', 'boilerplate']),
    parser.add_argument('-i', '--inplace', action='store_true')
    args = parser.parse_args(sysargv[1:])
    return args

def main():
    """
    Main function to execute the evn module.
    """
    import sys

    args = get_args(sys.argv)

    if args.filter:
        for input_file in args.input:
            with open(input_file, 'r') as f:
                text = f.read()
            filtered_text = evn.filter_python_output(text, preset=args.filter)
            if args.inplace:
                with open(input_file, 'w') as f:
                    f.write(filtered_text)
            else:
                print(filtered_text)
    else:
        # Default behavior, just print the inputs
        for input_file in args['input']:
            with open(input_file, 'r') as f:
                print(f.read())

if __name__ == '__main__':
    main()

#!/usr/bin/env python3

import os
import html
import json
import mimetypes
import traceback

from wsgiref.handlers import read_environ
from wsgiref.simple_server import make_server

import main as solver

LOCATION = os.path.realpath(os.path.dirname(__file__))


def parse_post(environ):
    """ takes in a dictionary that contains the HTTP server request information
        parses the contents of the request's body and returns it's json format
    """
    try:
        body_size = int(environ.get("CONTENT_LENGTH", 0))
    except:
        body_size = 0

    body = environ["wsgi.input"].read(body_size)
    try:
        return json.loads(body)
    except:
        return {}

# def find_region(n, r, c):
#     """(slowly) find which region (as a set of locations) the given coordinates are in [0, n)"""
#     for i in range(n):
#         locs = set(subgrid_locs(n, i))
#         if (r,c) in locs:
# 
#             return locs


def check_sudoku(original, result, expect_none=False):
    if expect_none: 
        assert result is None
    else: 
        assert result is not None
        n = len(original)

        # assert that the returned board and orginal board have same dimensions
        assert len(result) == n
        assert all(len(row) == n for row in result)

        sn = int(n**0.5)
        all_nums = set(range(1, n + 1))
        

        # assert that the the board is solved such that only all empty spaces are filled in resulting board
        assert all(
            (iv == jv or iv == 0)
            for i, j in zip(original, result)
            for iv, jv in zip(i, j)
        )

        # asserts that each row contains no duplicates
        assert all(set(i) == all_nums for i in result)

        # asserts that each column contains no duplicates
        for c in range(n):
            assert {i[c] for i in result} == all_nums
        
        # asserts that each subgrid contains no duplicates
        for sr in range(sn):
            for sc in range(sn):
                assert {
                    result[r][c]
                    for r in range(sr * sn, (sr + 1) * sn)
                    for c in range(sc * sn, (sc + 1) * sn)
                } == all_nums

def victory_check(payload):
    """Takes in a dictionary as input and checks whether the board is of the correct dimensions"""
    board = payload['board']
    empty_board = [[0] * len(board) for _ in board]
    try:
        assert board
        check_sudoku(empty_board, board)
        return {'victory': True}
    except AssertionError:
        return {'victory': False}

def solve(payload):
    """takes in a 2D list sudoku board and returns a solved sudoku board as a 2D list"""

    board = payload
    formula = solver.sudoku_board_to_sat_formula(board)
    assignments = solver.satisfying_assignment(formula)
    sol = solver.assignments_to_sudoku_board(assignments, len(board))
    return sol


funcs = {
    'victory_check': victory_check,
    'solve': solve,
}

def application(environ, start_response):
    path = (environ.get("PATH_INFO", "") or "").lstrip("/")
    if path in funcs:
        try:
            out = funcs[path](parse_post(environ))
            body = json.dumps(out).encode("utf-8")
            status = "200 OK"
            type_ = "application/json"
        except Exception as e:
            tb = traceback.format_exc()
            print(
                "--- Python error (likely in your solver code) during the next operation:\n"
                + tb,
                end="",
            )
            body = html.escape(tb).encode("utf-8")
            status = "500 INTERNAL SERVER ERROR"
            type_ = "text/plain"
    else:
        if path == "":
            static_file = "sudoku.html"
        else:
            static_file = path

        test_fname = os.path.join(LOCATION, 'ui', static_file)
        try:
            status = "200 OK"
            with open(test_fname, "rb") as f:
                body = f.read()
            type_ = mimetypes.guess_type(test_fname)[0] or "text/plain"
        except FileNotFoundError:
            status = "404 FILE NOT FOUND"
            body = test_fname.encode("utf-8")
            type_ = "text/plain"

    len_ = str(len(body))
    headers = [("Content-type", type_), ("Content-length", len_)]
    start_response(status, headers)
    return [body]


if __name__ == "__main__":
    # Initialize the WSGI server on the specified port
    PORT = 6101
    print(f"starting server.  navigate to http://localhost:{PORT}/")
    with make_server("", PORT, application) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("Shutting down.")
            httpd.server_close()

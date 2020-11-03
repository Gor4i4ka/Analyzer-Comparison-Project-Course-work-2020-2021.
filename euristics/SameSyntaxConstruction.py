import clang
import clang.cindex as ci
import typing
import sys

from projectLib.Comparison import Comparison
from projectLib.AnalyzerInfo import AnalyzerInfo

index = clang.cindex.Index.create()
translation_unit = index.parse('/home/gorchichka/cplus/dummy.cpp', args=['-std=c++17'])


def find_typerefs(node, typename):
    """ Find all references to the type named 'typename'
    """
    if node.kind.is_reference():
        ref_node = clang.cindex.Cursor_ref(node)
        if ref_node.spelling == typename:
            print ('Found %s [line=%s, col=%s]' % (
                typename, node.location.line, node.location.column))
    # Recurse for children of this node
    for c in node.get_children():
        find_typerefs(c, typename)

#print ('Translation unit:', translation_unit.spelling)
#find_typerefs(translation_unit.cursor, "")

def find_if(node: clang.cindex.Cursor, mode):
    if mode:
        print(node.kind)

    if node.kind == clang.cindex.CursorKind.IF_STMT:
        print(node.kind)
        ifstmt = node.referenced
        print("{} {}".format(node.location.line, node.location.column))
        controlled_stmt = list(node.get_children())[1]
        print("{} {}".format(controlled_stmt.location.line, controlled_stmt.location.column))



    for c in node.get_children():
        find_if(c, False)


def same_syntax_construction(analyzer1_info: AnalyzerInfo, analyzer2_info: AnalyzerInfo, eur_params: dict):

    if analyzer1_info.info_type != "combined" or analyzer2_info.info_type != "combined":
        print("WRONG INFO TYPE FOR EURISTICS LINES")
        return -1

    result_comparison = Comparison()
    result_comparison.fill_for_euristics(analyzer1_info, analyzer2_info)

find_if(translation_unit.cursor, False)


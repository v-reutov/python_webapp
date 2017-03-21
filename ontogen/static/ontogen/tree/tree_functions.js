function tree_expand_all(tree_id) {
    $('#' + tree_id).jstree('open_all');
};
function tree_collapse_all(tree_id) {
    $('#' + tree_id).jstree('close_all');
};

function refresh_tree(tree_id) {
    $('#' + tree_id).jstree('refresh');
}

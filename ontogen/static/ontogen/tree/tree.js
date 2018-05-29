$(function () {
	$('#tree')
		.on('loaded.jstree', function (e, data) {
			tree_expand_all('tree');
		})
		.on('select_node.jstree', function (e, data) {
			if ($('#' + data.node.parent)[0].className.match(/select-single/)) {
				// Deselect all other nodes on the same level
				var selected = data.node.id;
				var siblings = data.instance.get_node(data.node.parent).children;

				var index;
				for (index = 0; index < siblings.length; index++) {
					var node = data.instance.get_node(siblings[index]);
					if (node.id != selected) {
						data.instance.uncheck_node(node.id);
					}
				}
			}
		})
		.on('deselect_node.jstree', function (e, data) {
			return true;
		})
		.jstree({
			"core": {
				"data": {
					"url": './tree/',
					"dataType": "json",
					"data": function (node) {
						return {
							"id": node.id
						};
					},
				},
				"animation": 0,
				"check_callback": true,
				"themes": {
					"name": "proton",
					"responsive": true
				}
			},
			"checkbox": {
				"keep_selected_style": true,
				"three_state": false
			},
			"contextmenu": {
				"select_node": false,
				"items": function ($node) {

					active_node = $node;

					if (active_node["type"] == "default")
						return null;

					url = active_node["id"].replace(/(\d+)/, '/$1/');
					modal = document.getElementById('modal-info');

					modal_load = function (content_url) {
						$('#modal-content').load(content_url, function () {
							var hide_modal = function () {
								modal.style.display = "none";
							};
							var submit_form = function () {
								$('.django-ckeditor-widget textarea').each(function () {
									var textarea = $(this);
									var editor = CKEDITOR.instances[textarea.attr('id')];

									if (editor !== undefined) {
										textarea.val(editor.getData());
									}
								});

								$.post(content_url, $('#form').serialize(), function (response) {
									if (response == "OK") {
										modal.style.display = "none";
										refresh_tree('tree');
									} else {
										$("#modal-content").html(response);
										document.getElementById("submit-form-button").onclick = submit_form;
										document.getElementById("modal-close").onclick = hide_modal;
									}
								});
							};
							var submit = document.getElementById("submit-form-button")
							var close = document.getElementById("modal-close")

							if (submit != null) submit.onclick = submit_form;
							if (close != null) close.onclick = hide_modal;

							modal.style.display = "block";
						});
					}

					var items = {
						getDetails: {
							"separator_after": true,
							"label": gettext("Details"),
							"action": function (data) {
								modal_load(url);
							}
						},
						createNode: {
							"label": gettext("Add"),
							"action": function (obj) {
								url = active_node["type"].match(/(\w+)-container/)[1] + "/add/"
								modal_load(url);
							}
						},
						editNode: {
							"label": gettext("Edit"),
							"action": function (obj) {
								url = url + "edit/"
								modal_load(url);
							}
						},
						deleteNode: {
							"label": gettext("Remove"),
							"action": function (obj) {
								url = url + "delete/"
								modal_load(url);
							}
						}
					};

					if (!active_node["type"].match(/-container/)) {
						delete items.createNode
					} else {
						delete items.editNode
						delete items.deleteNode
						delete items.getDetails
					}

					return items;
				}
			},
			"conditionalselect": function (node) {
				return node.children.length == 0;
			},
			"types": {
				"pattern": {
					"icon": false //"glyphicon glyphicon-file"
				},
				"instruction": {
					"icon": false //"glyphicon glyphicon-file"
				},
				"data": {
					"icon": "glyphicon glyphicon-file"
				},
				"pattern-container": {},
				"instruction-container": {},
				"default": {}
			},
			"plugins": [
				"contextmenu", "types", "checkbox", "conditionalselect",
				// "wholerow"
			]
		});
});
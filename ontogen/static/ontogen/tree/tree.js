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
					if (node.id !== selected) {
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
					}
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

					var active_node = $node;
                    var type = active_node.type;

					if (type === "default" || type === "multimedia-container")
						return null;

					var url = active_node["id"].replace(/(\d+)/, '/$1/');
					var modal = document.getElementById('modal-info');

					var modal_load = function (content_url) {
						$('#modal-content').load(content_url, function (response, status) {
						    if (status === "error") {
						        alert("Произошла ошибка :(");

                                return;
                            }

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

                                var form = $('#form')[0];

                                $.ajax({
                                    url: content_url,
                                    data: new FormData(form),
                                    processData: false,
                                    contentType: false,
                                    type: 'POST',
                                    success: function (response) {
                                        if (response === "OK") {
                                            modal.style.display = "none";
                                            refresh_tree('tree');
                                        } else if (response.errors !== undefined) {
                                            $(".errorlist").empty();
                                            _.each(response.errors, function (item) {
                                                $(".errorlist").append('<li>' + item + '</li>');
                                            });
                                        } else {
                                            $("#modal-content").html(response);
                                            document.getElementById("submit-form-button").onclick = submit_form;
                                            document.getElementById("modal-close").onclick = hide_modal;
                                        }
                                    }
                                });
                                // $.post(content_url, new FormData(form), function (response) {
                                 //    if (response === "OK") {
                                 //        modal.style.display = "none";
								// 		refresh_tree('tree');
								// 	} else {
								// 		$("#modal-content").html(response);
								// 		document.getElementById("submit-form-button").onclick = submit_form;
								// 		document.getElementById("modal-close").onclick = hide_modal;
								// 	}
								// });
							};
							var submit = document.getElementById("submit-form-button");
							var close = document.getElementById("modal-close");

							if (submit != null) submit.onclick = submit_form;
							if (close != null) close.onclick = hide_modal;

							modal.style.display = "block";
						});
					};

					var items = { };

					if (active_node["type"].match(/-container/)) {
						items = {
                            createNode: {
                                "label": gettext("Add"),
                                "action": function (obj) {
                                    url = active_node["type"].match(/(\w+)-container/)[1] + "/add/"
                                    modal_load(url);
                                }
                            }
                        };
                    } else {
                        items = {
                            getDetails: {
                                "separator_after": true,
                                "label": gettext("Details"),
                                "action": function (data) {
                                    modal_load(url);
                                }
                            },
                            editNode: {
                                "label": gettext("Edit"),
                                "action": function (obj) {
                                    modal_load(url + "edit/");
                                }
                            },
                            deleteNode: {
                                "label": gettext("Remove"),
                                "action": function (obj) {
                                    modal_load(url + "delete/");
                                }
                            }
                        };
					}

					return items;
				}
			},
			"conditionalselect": function (node) {
				// return node.children.length === 0;
				return !node.original.type.match(/-container/)
					&& (node.li_attr.class === undefined || !node.li_attr.class.includes('no-select'));
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
				"frameset": {
                    "icon": "glyphicon glyphicon-file"
				},
				"pattern-container": {},
				"instruction-container": {},
				"multimedia-container": {},
                "frameset-container": {},
				"default": {}
			},
			"plugins": [
				"contextmenu", "types", "checkbox", "conditionalselect"
				// "wholerow"
			]
		});
});
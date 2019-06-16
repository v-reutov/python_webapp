var ontologies = {
    subject: '',
    task: ''
};

var networks = {
    subject: undefined,
    task: undefined
};

var jcrop_api;
var jcrop_enabled = true;
var jcrop_target;

var crop_object = undefined;
var previewXStart;
var previewYStart;
var previewHeight;
var previewWidth;

var detailsCount;

var currentTab = 0; // Current tab is set to be the first tab (0)

$(document).ready(function () {
    showTab(currentTab); // Display the current tab

    function saveTextAsFile(prefix) {
        var textToWrite = ontologies[prefix];
        var textFileAsBlob = new Blob([textToWrite], {
            type: 'text/plain'
        });
        var fileNameToSaveAs = prefix + "-ontology.ont";
        var downloadLink = document.createElement("a");

        downloadLink.download = fileNameToSaveAs;
        downloadLink.innerHTML = "My Hidden Link";
        window.URL = window.URL || window.webkitURL;
        downloadLink.href = window.URL.createObjectURL(textFileAsBlob);
        downloadLink.onclick = destroyClickedElement;
        downloadLink.style.display = "none";
        document.body.appendChild(downloadLink);
        downloadLink.click();
    }

    function destroyClickedElement(event) {
        document.body.removeChild(event.target);
    }

    $("#download-subject").click(function (e) {
        e.preventDefault();
        saveTextAsFile("subject");
    });

    $("#download-task").click(function (e) {
        e.preventDefault();
        saveTextAsFile("task");
    });

    $('img').each(function () {
        this.onclick = function () {
            if (!jcrop_enabled) return;
            if (jcrop_target === this) return;

            destroyJcropIfAny();

            jcrop_target = this;

            $(this).Jcrop({
                    // onChange: updatePreview,
                    onSelect: onSelectChanged
                }, function () {
                    jcrop_api = this;
                }
            );
        }
    });

    $(document).keyup(function (e) {
        if (e.keyCode === 27) {
            destroyJcropIfAny();
        }
    });

    var canvas = $("#preview")[0];

    canvas.width = 400;
    canvas.height = 250;

    canvas.style.height = canvas.height;
    canvas.style.width = canvas.width;

    $('#task-modal').on('show.bs.modal', function (e) {
        var methodCombo = document.getElementById('vis-method-combo');
        var resourceCombo = document.getElementById('vis-resource-combo');

        methodCombo.value = "animation";
        onVisMethodChange();
    })
});

function destroyJcropIfAny() {
    if (jcrop_api !== undefined) {
        jcrop_api.destroy();
    }
    
    jcrop_api = undefined;
    crop_object = undefined;
    jcrop_target = undefined;

    $('#upload-image-action').addClass('disabled');
}

function updatePreview(crop) {
    if (parseInt(crop.w) > 0) {
        crop_object = crop;

        // Show image preview
        var canvas = $("#preview")[0];
        var context = canvas.getContext("2d");
        context.clearRect(0, 0, canvas.width, canvas.height);

        fitImageOn(canvas, jcrop_target, crop);
    }
}

function onSelectChanged(crop) {
    if (parseInt(crop.w) > 0) {
        updatePreview(crop);
        recognizeNumber();

        $('#upload-image-action').removeClass('disabled');
    }
}

function fitImageOn(canvas, imageObj, crop) {
    var context = canvas.getContext("2d");

    var imageAspectRatio = crop.w / crop.h;
    var canvasAspectRatio = canvas.width / canvas.height;
    var renderableHeight, renderableWidth, xStart, yStart;

    if (imageAspectRatio < canvasAspectRatio) {
        renderableHeight = canvas.height;
        renderableWidth = crop.w * (renderableHeight / crop.h);
        xStart = (canvas.width - renderableWidth) / 2;
        yStart = 0;
    }

    else if (imageAspectRatio > canvasAspectRatio) {
        renderableWidth = canvas.width;
        renderableHeight = crop.h * (renderableWidth / crop.w);
        xStart = 0;
        yStart = (canvas.height - renderableHeight) / 2;
    }

    else {
        renderableHeight = canvas.height;
        renderableWidth = canvas.width;
        xStart = 0;
        yStart = 0;
    }

    previewXStart = xStart;
    previewYStart = yStart;
    previewHeight = renderableHeight;
    previewWidth = renderableWidth;

    context.drawImage(jcrop_target, crop.x, crop.y, crop.w, crop.h, xStart, yStart, renderableWidth, renderableHeight);
}

function recognizeNumber() {
    var canvas = document.getElementById("preview");
    var context = canvas.getContext("2d");

    var imageData = context.getImageData(previewXStart, previewYStart, previewWidth, previewHeight);

    var regex = /\d+/g;

    OCRAD(imageData, {
        numeric: true
    }, function (text) {
        var result;
        while ((result = regex.exec(text)) !== null) {
            if (result[0] > 0 && result[0] <= detailsCount) {
                $('#subject-combo').val(result[0]);
                break;
            }
        }
    })
}

function buildOntology(kind) {
    var text = window.getSelection().toString();

    if (text === undefined || text === "") {
        alert(strings.text_not_selected);
        return;
    }

    var post_data = {
        'text': text,
        'patterns': patterns
    };

    if (kind === "subject") {
        buildSubjectOntology(post_data);
    } else if (kind === "task") {
        buildTaskOntology(post_data);
    } else {
        alert("Unknown kind of ontology");
    }
}

function reportError(response) {
    if (response.error !== undefined) {
        alert(response.error)
    } else {
        alert('Something went wrong')
    }
}

function updateButtonLoaderUi(kind, disabled) {
    $('#build-'+ kind +'-button').prop('disabled', disabled)

    if (disabled)
        $('#build-'+ kind +'-loader').show();
    else
        $('#build-'+ kind +'-loader').hide();
}

function buildSubjectOntology(data) {
    var url = urls.generate_subject;
    var container = document.getElementById('subject');

    updateButtonLoaderUi('subject', true);

    $.post(url, data, function (response) {
        if (response.status === "OK") {
            ontologies.subject = response.result;
            var result = loadOntologyToContainer(container, response.result);
            networks.subject = result.network;

            loadSubjectCombo(response.subject_nodes);
        } else {
            reportError(response);
        }

        updateButtonLoaderUi('subject', false);
    });
}

function addComboOption(combo, value, html, dataLabel) {
    var opt = document.createElement('option');
    opt.innerHTML = html;
    opt.dataset.label = dataLabel;
    opt.value = value;

    combo.appendChild(opt);
}

function loadSubjectCombo(subject_nodes) {
    detailsCount = 0;

    var combo = document.getElementById('subject-combo');

    $(combo).empty();
    _.each(subject_nodes, function (item) {
        addComboOption(combo, item.number, item.number + ": " + item.name, item.name);
        detailsCount += 1;
    });

    $('#subject-combo').prop('disabled', false);
    $('#populate-subject-button').prop('disabled', false);
    $('#build-task-button').prop('disabled', false);
}

function loadTaskCombo(task_nodes) {
    var combo = document.getElementById('task-combo');

    $(combo).empty();

    _.each(task_nodes, function (item, index) {
        var opt = document.createElement('option');
        addComboOption(combo, index, (index + 1) + ": " + item.name, item.name);
    });

    $('#task-combo').prop('disabled', false);
    $('#populate-task-button').prop('disabled', false);
    $('#build-task-button').prop('disabled', false);
    $('#download-subject').prop('disabled', false);
    $('#download-task').prop('disabled', false);
}

function loadOntologyToContainer(container, ontology) {
    var result = initializeOntology(container, ontology);

    container.getElementsByClassName('vis-network')[0].style.position = 'absolute';

    setTimeout(function () {
        result.network.fit();
        $('#ontology-container').show();
    }, 500);

    return result;
}

function buildTaskOntology(data) {
    var url = urls.generate_task;
    var subject_container = document.getElementById('subject');
    var task_container = document.getElementById('task');

    data["subject"] = ontologies.subject;

    updateButtonLoaderUi('task', true);

    $.post(url, data, function (response) {
        if (response.status === "OK") {
            ontologies = response.result;

            var subject = loadOntologyToContainer(subject_container, response.result.subject);
            var task = loadOntologyToContainer(task_container, response.result.task);

            networks.subject = subject.network;
            networks.task = task.network;

            loadTaskCombo(response.result.task_nodes);
        } else {
            reportError(response);
        }

        updateButtonLoaderUi('task', false);
    });
}


function showTab(n) {
    // This function will display the specified tab of the form ...
    var x = document.getElementsByClassName("tab");
    x[n].style.display = "block";
    // ... and fix the Previous/Next buttons:
    document.getElementById("prevBtn").disabled = n === 0;
    document.getElementById("nextBtn").disabled = n === (x.length - 1);
}

function nextPrev(n) {
    // This function will figure out which tab to display
    var x = document.getElementsByClassName("tab");
    x[currentTab].style.display = "none";

    // Increase or decrease the current tab by 1:
    currentTab = currentTab + n;
    // if you have reached the end of the form... :
    if (currentTab >= x.length) {
        return false;
    }
    // Otherwise, display the correct tab:
    showTab(currentTab);
}

function exportCroppedImg() {
    // create a temporary canvas sized to the cropped size
    var canvas1 = document.createElement('canvas');
    var ctx1 = canvas1.getContext('2d');
    canvas1.width = crop_object.w;
    canvas1.height = crop_object.h;

    // use the extended from of drawImage to draw the
    // cropped area to the temp canvas
    ctx1.drawImage(
        jcrop_target,
        crop_object.x, crop_object.y, crop_object.w, crop_object.h,
        0, 0, crop_object.w, crop_object.h);

    // return the .toDataURL of the temp canvas
    return canvas1.toDataURL();
}

function upload_image() {
    if (crop_object === undefined) return;

    var url = urls.populate_subject_with_image;

    var combo = document.getElementById('subject-combo');
    var node = combo.options[combo.selectedIndex].dataset.label;

    var data = {
        'node': node,
        'subject': ontologies.subject,
        'image': exportCroppedImg()
    };

    $.post(url, data, function (response) {
        if (response.status === "OK") {
            ontologies.subject = response.result.subject;
            loadOntologyToContainer($("#subject")[0], ontologies.subject);
        } else {
            reportError(response);
        }
    });
}

function refreshNetwork() {
    if ($('#subject').hasClass('active')) {
        if (networks.subject !== undefined) {
            networks.subject.fit();
        }
    } else {
        if (networks.task !== undefined) {
            networks.task.fit();
        }
    }
}

function onVisMethodChange() {
    var combo = $('#vis-resource-combo');
    var methodCombo = $('#vis-method-combo');
    var submit = $('#task-modal-submit');

    var value = methodCombo.val();

    function updateUi(disabled) {
        combo.prop('disabled', disabled);
        submit.prop('disabled', disabled);
    }

    if (value === "animation") {
        $.get(urls.get_all_framesets, function (data) {
            var framesets = data.framesets;

            combo.empty();

            framesets.reverse();

            _.each(framesets, function (item) {
                addComboOption(combo[0], item.id, item.text);
            });

            updateUi(false);
        });
    } else {
        updateUi(true);

        combo.empty();
        addComboOption(combo[0], -1, "Метод временно не поддерживается");
    }
}

function populateTaskOntology() {
    var resourceCombo = $('#vis-resource-combo');
    var methodCombo = $('#vis-method-combo');
    var stepCombo = $('#task-combo');

    var method = methodCombo.val();
    var resource = resourceCombo.val();

    var data = {
        task: ontologies.task,
        step_index: stepCombo.val(),
        method: method,
        resource: resource
    };

    var container = document.getElementById('task');

    $.post(urls.populate_task_with_method, data, function (response) {
        if (response.status === "OK") {
            ontologies.task = response.result.task;
            var result = loadOntologyToContainer(container, response.result.task);
            networks.task = result.network;

            $('#task-modal').modal('hide');
        } else {
            reportError(response);
        }
    });
}
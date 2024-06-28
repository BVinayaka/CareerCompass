document.querySelector('#page').contentEditable = true;

defaultTemplateVars = [ "fontDroid" , "caseNormal" , "titleRuled" , "ruleAbove" , "imageShow" , "rollShow" , "course1" , "tableShow" , "edyearFirst" , "experience1" , "projects1" ]

$('.toggle-option').click(function(){
	toggleType = $(this).attr('data-toggle');
	toggleValue = $(this).attr('id');
	if(!$(this).hasClass('multi-select'))
	{
		if(!$(this).hasClass('selected'))
		{
			$('.toggle-option',$(this).parent()).removeClass('selected');
			$(this).addClass('selected');
			changeTemplate(toggleType,toggleValue);
		}
	}
	else
	{
		if($(this).hasClass('selected'))
			$(this).removeClass('selected');
		else
			$(this).addClass('selected');
		changeTemplate(toggleType,toggleValue);
	}
});

$('input[name="sectionToggle"]').change(function(){
	toggleSection($(this).val(),$(this).is(':checked'));
});


function template(value)
{
	if(value=='default')
	{
		$('#defaultTemplateBtn').removeClass('btn-default').addClass('btn-danger');
		$('#customTemplateBtn').removeClass('btn-danger').addClass('btn-default');
		$('#customTemplateOptions').hide();
		for(i=0;i<defaultTemplateVars.length;i++)
			$('#'+defaultTemplateVars[i]).click();
	}
	else
	{
		$('#customTemplateBtn').removeClass('btn-default').addClass('btn-danger');
		$('#defaultTemplateBtn').removeClass('btn-danger').addClass('btn-default');
		$('#customTemplateOptions').show();
	}
}

function toggleSection(sectionName,toggleState)
{
	if(toggleState==true)
		$('input[value="'+sectionName+'"]').attr('checked','true');
	else
		$('input[value="'+sectionName+'"]').removeAttr('checked');
	$('#'+sectionName).toggle();
}

function changeTemplate(toggleType,toggleValue)
{
	switch(toggleType)
	{
		case 'minor':
			if(toggleValue=='minorShow')
			{
				$('#contentMinor').show();
				$('#image_box').css('margin-top','35px');
			}
			else
			{
				$('#contentMinor').hide();
				$('#image_box').css('margin-top','25px');
			}
			break;
		case 'contact':
			if(toggleValue=='contact3')
			{
				$('#contactLink1').hide();
				$('#contactLink2').hide();
			}
			else if(toggleValue=='contact4')
			{
				$('#contactLink1').show();
				$('#contactLink2').hide();
			}
			else
			{
				$('#contactLink1').show();
				$('#contactLink2').show();
			}
			break;
		case 'margin':
			if(toggleValue=='margin1')
				$('#page').css('padding','0.2cm 1cm 1cm 1cm');
			else if(toggleValue=='margin2')
				$('#page').css('padding','0.2cm 1.1cm 1cm 1.1cm');
			else if(toggleValue=='margin3')
				$('#page').css('padding','0.2cm 1.2cm 1cm 1.2cm');
			else if(toggleValue=='margin4')
				$('#page').css('padding','0.2cm 1.3cm 1cm 1.3cm');
			else if(toggleValue=='margin5')
				$('#page').css('padding','0.2cm 1.4cm 1cm 1.4cm');
			else if(toggleValue=='margin6')
				$('#page').css('padding','0.2cm 1.5cm 1cm 1.5cm');
			break;
		case 'line':
			if(toggleValue=='line1')
				$('#page').css('line-height','1.1em');
			else if(toggleValue=='line2')
				$('#page').css('line-height','1.2em');
			else if(toggleValue=='line3')
				$('#page').css('line-height','1.3em');
			else if(toggleValue=='line4')
				$('#page').css('line-height','1.4em');
			else if(toggleValue=='line5')
				$('#page').css('line-height','1.5em');
			else if(toggleValue=='line6')
				$('#page').css('line-height','1.6em');
			break;
		case 'column':
			if(toggleValue=='column1')
				$('.table tbody tr td:nth-child(1)').toggleClass('text-center');
			else if(toggleValue=='column2')
				$('.table tbody tr td:nth-child(2)').toggleClass('text-center');
			else if(toggleValue=='column3')
				$('.table tbody tr td:nth-child(3)').toggleClass('text-center');
			else if(toggleValue=='column4')
				$('.table tbody tr td:nth-child(4)').toggleClass('text-center');
			break;

		case 'font':
			if(toggleValue=='fontVerdanaSans')
				$('#page').removeClass('droid').removeClass('roboto').removeClass('verdana-serif').addClass('verdana-sans');
			else if(toggleValue=='fontVerdanaSerif')
				$('#page').removeClass('verdana-sans').removeClass('droid').removeClass('roboto').addClass('verdana-serif');
			else if(toggleValue=='fontRoboto')
				$('#page').removeClass('verdana-serif').removeClass('verdana-sans').removeClass('droid').addClass('roboto');
			else if(toggleValue=='fontDroid')
				$('#page').removeClass('roboto').removeClass('verdana-serif').removeClass('verdana-sans').addClass('droid');
			break;
		case 'case':
			if(toggleValue=='caseNormal')
				$('.section-title').removeClass('uppercase');
			else
				$('.section-title').addClass('uppercase');
			break;
		case 'title':
			if(toggleValue=='titleRuled')
			{
				$('.section-title').removeClass('shaded');
				$('.section-title').addClass('ruled');
			}
			else
			{
				$('.section-title').removeClass('ruled');
				$('.section-title').addClass('shaded');
			}
			break;
		case 'rule':
			if(toggleValue=='ruleAbove')
			{
				$('.section-title').removeClass('rule-below');
				$('.section-title').addClass('rule-above');
			}
			else
			{
				$('.section-title').removeClass('rule-above');
				$('.section-title').addClass('rule-below');
			}
			break;

		case 'image':
			if(toggleValue=='imageShow')
			{
				$('#image_box').show();
				$('#info').css('margin-left','0px');
			}
			else
			{
				$('#image_box').hide();
				$('#info').css('margin-left','20px');
			}
			break;
		case 'roll':
			if(toggleValue=='rollShow')
			{
				$('#contentRoll').show();
				$('#info').css('margin-top','0px');
			}
			else
			{
				$('#contentRoll').hide();
				$('#info').css('margin-top','10px');
			}
			break;
		case 'course':
			if(toggleValue=='course1')
			{
				$('#contentBranch').hide();
				$('#contentCourse').text('B.Tech - '+$('#contentBranch').text());
			}
			else
			{
				$('#contentBranch').show();
				$('#contentCourse').text('B.Tech undergraduate');
			}
			break;
		case 'table':
			if(toggleValue=='tableShow')
			{
				$('#educationTable').removeClass('borderless');
				$('#educationTable').addClass('customBordered');
			}
			else
			{
				$('#educationTable').removeClass('customBordered');
				$('#educationTable').addClass('borderless');
			}
			break;
		case 'edyear':
			if(toggleValue=='edyearFirst')
			{
				$("#educationTable tr").each(function () {
					$(this).find("td").eq(0).before($(this).find("td").eq(3));
				});
				var temp = document.getElementById('column4').className;
				document.getElementById('column4').className = document.getElementById('column3').className;
				document.getElementById('column3').className = document.getElementById('column2').className;
				document.getElementById('column2').className = document.getElementById('column1').className;
				document.getElementById('column1').className = temp;
			}
			else
			{
				$("#educationTable tr").each(function () {
					$(this).find("td").eq(3).after($(this).find("td").eq(0));
				});
				var temp = document.getElementById('column1').className;
				document.getElementById('column1').className = document.getElementById('column2').className;
				document.getElementById('column2').className = document.getElementById('column3').className;
				document.getElementById('column3').className = document.getElementById('column4').className;
				document.getElementById('column4').className = temp;
			}
			break;
		case 'experience':
			if(toggleValue=='experience1')
			{
				$("#sectionExperience .title , #sectionExperience .time").css('display','inline-block');
				$("#sectionExperience .time").addClass('right').removeClass('tab');
				$("#sectionExperience .link").show();
			}
			else
			{
				$("#sectionExperience .title , #sectionExperience .time").css('display','block');
				$("#sectionExperience .time").removeClass('right').addClass('tab');
				$("#sectionExperience .link").hide();
			}
			break;
		case 'projects':
			if(toggleValue=='projects1')
			{
				$("#sectionProjects .title , #sectionProjects .time").css('display','inline-block');
				$("#sectionProjects .time").addClass('right').removeClass('tab');
				$("#sectionProjects .mentor , #sectionProjects .link").show();
			}
			else
			{
				$("#sectionProjects .title , #sectionProjects .time").css('display','block');
				$("#sectionProjects .time").removeClass('right').addClass('tab');
				$("#sectionProjects .mentor , #sectionProjects .link").hide();
			}
			break;
	}
}

function insertList()
{
	node = getSelectionContainerElement();
	var ul = document.createElement("ul");
	ul.className = 'decimal';
	ul.style.marginLeft = '0px';
	ul.innerHTML = "<li>Sub-point 1 : Description</li><li>Sub-point 2 : Description</li>";
	insertAfter(node,ul);
}

function decreaseIndent()
{
	node = getSelectionContainerElement();
	while(node.tagName!='UL')
		node = node.parentNode;
	node.style.paddingLeft = parseInt(window.getComputedStyle(node).getPropertyValue("padding-left"))-5;
}

function increaseIndent()
{
	node = getSelectionContainerElement();
	while(node.tagName!='UL')
		node = node.parentNode;
	node.style.paddingLeft = parseInt(window.getComputedStyle(node).getPropertyValue("padding-left"))+5;
}

function changeListStyle(value)
{
	node = getSelectionContainerElement();
	while(node.tagName!='UL')
		node = node.parentNode;
	node.className = value;

}


function getSelectionContainerElement()
{
	var range, sel, container;
	if (document.selection && document.selection.createRange)
	{
		range = document.selection.createRange();
		return range.parentElement();
	}
	else if (window.getSelection)
	{
		sel = window.getSelection();
		if (sel.getRangeAt)
		{
			if (sel.rangeCount > 0)
				range = sel.getRangeAt(0);
		}
		else
		{
			
			range = document.createRange();
			range.setStart(sel.anchorNode, sel.anchorOffset);
			range.setEnd(sel.focusNode, sel.focusOffset);
			
			if (range.collapsed !== sel.isCollapsed)
			{
				range.setStart(sel.focusNode, sel.focusOffset);
				range.setEnd(sel.anchorNode, sel.anchorOffset);
			}
		}
		if (range)
		{
			container = range.commonAncestorContainer;
			return container.nodeType === 3 ? container.parentNode : container;
		}
	}
}

function insertAfter(referenceNode,newNode) {
    referenceNode.parentNode.insertBefore(newNode, referenceNode.nextSibling);
}

document.getElementById('image_box').addEventListener('click', function() {
	document.getElementById('file_input').click();
});
 
 




function generatePDF() {
    
    const options = {
        margin: [0, 0], 
        filename: 'RESUME.pdf',
        image: { type: 'jpeg', quality: 0.98 },
        html2canvas: { scale: 2 },
        jsPDF: { unit: 'in', format: 'a4', orientation: 'portrait' }, 
        pagebreak: { mode: ['avoid-all'] },
        html2pdf: { font: { size: 10 } } 
    };

    
    const content = document.getElementById('page');

 
    html2pdf()
        .from(content)
        .set(options)
        .save();
}


document.getElementById('downloadPDF').addEventListener('click', function() {
    generatePDF(); 
});




var referencesCheckbox = document.querySelector('input[name="sectionToggle"][value="sectionFooterMessage"]');

var referencesDiv = document.getElementById('referencesMessage');

referencesCheckbox.addEventListener('change', function() {
 
  if (this.checked) {
    referencesDiv.style.display = 'block';
  } else {
    referencesDiv.style.display = 'none';
  }
});

function closeSectionToggleModal() {
  var modal = document.getElementById('referencesMessage');
  modal.style.display = 'none';  
}

function toggleUsageInstructions() {
  var instructionsDiv = document.getElementById('usageInstructions');
  if (instructionsDiv.style.display === 'none') {
    instructionsDiv.style.display = 'block';
  } else {
    instructionsDiv.style.display = 'none';
  }
}

function closeUsageInstructions() {
  var modal = document.getElementById('usageInstructions');
  modal.style.display = 'none';
}


function openSectionToggleModal() {
  var instructionsDiv = document.getElementById('sectionToggleModal');
  if (instructionsDiv.style.display === 'none') {
    instructionsDiv.style.display = 'block';
  } else {
    instructionsDiv.style.display = 'none';
  }
}

// Function to close the modal
function closeSectionToggleModal() {
  document.getElementById('sectionToggleModal').style.display = 'none';
}

  $(document).ready(function () {
	var video = document.getElementById('video');
	var canvas = document.getElementById('canvas');
	var context = canvas.getContext('2d');

	// Open camera button click event
	document.getElementById('openCamera').addEventListener('click', function () {
		// Show the video element
		video.style.display = 'block';
		// Show the capture button
		document.getElementById('capture').style.display = 'block';

		// Open the camera
		navigator.mediaDevices.getUserMedia({ video: true })
			.then(function (stream) {
				video.srcObject = stream;
				video.play();
			})
			.catch(function (err) {
				console.log("An error occurred: " + err);
			});
	});

	// Capture button click event
	document.getElementById('capture').addEventListener('click', function () {
		// Draw the captured frame onto the canvas
		context.drawImage(video, 0, 0, 640, 480);

		// Stop the camera
		video.srcObject.getTracks().forEach(track => track.stop());

		// Hide the video element and capture button
		video.style.display = 'none';
		document.getElementById('capture').style.display = 'none';

		// Convert the canvas data to base64 format
		var imageData = canvas.toDataURL('image/png');

		// Send the captured image data to the server
		$.ajax({
			url: '/process_photo',
			type: 'POST',
			data: { imageData: imageData },
			success: function (response) {
				// Display the processed image
				var outputImage = document.getElementById('output');
				outputImage.src = response.outputImage;
				outputImage.style.display = 'block';
			},
			error: function (xhr, status, error) {
				console.log("An error occurred: " + error);
				alert("NO head portion found")
			}
		});
	});
});
document.getElementById('openFile').addEventListener('click', function() {
    document.getElementById('fileInput').click();
});

$(document).ready(function () {
    var video = document.getElementById('video');
    var canvas = document.getElementById('canvas');
    var context = canvas.getContext('2d');

    // File input change event
    document.getElementById('fileInput').addEventListener('change', function (event) {
        var file = event.target.files[0];
        var reader = new FileReader();
        reader.onload = function (e) {
            // Convert the selected file to a base64 string
            var imageData = e.target.result;

            // Send the base64-encoded image data to the server
            $.ajax({
                url: '/process_photo',
                type: 'POST',
                data: { imageData: imageData },
                success: function (response) {
                    // Display the processed image
                    var outputImage = document.getElementById('output');
                    outputImage.src = response.outputImage;
                    outputImage.style.display = 'block';
                },
                error: function (xhr, status, error) {
					alert("NO head portion found")
                    console.log("An error occurred: " + error);
                }
            });
        };
        reader.readAsDataURL(file);
    });
});
function toggleChatbot() {
	const chatbotContainer = document.getElementById('chatbotContainer');
	const toggleButton = document.getElementById('toggleButton');

	if (chatbotContainer.style.display === 'none' || chatbotContainer.style.display === '') {
		chatbotContainer.style.display = 'flex';
		toggleButton.style.display = 'none';
	} else {
		chatbotContainer.style.display = 'none';
		toggleButton.style.display = 'block';
	}
}

function sendMessage() {
	const userInput = document.getElementById("userInput").value;

	if (userInput.trim() !== "") {
		displayMessage("user", userInput);

		const payload = {
			question: userInput,
		};

		fetch("/chat", {
			method: "POST",
			headers: {
				"Content-Type": "application/json",
			},
			body: JSON.stringify(payload),
		})
		.then((response) => {
			if (!response.ok) {
				throw new Error('Network response was not ok');
			}
			return response.json();
		})
		.then((data) => {
			const answer = data.answer;
			displayMessage("bot", answer);
			scrollChatToBottom();
		})
		.catch((error) => {
			console.error("Error:", error);
			displayMessage("bot", "Sorry, something went wrong.");
		});

		document.getElementById("userInput").value = "";
	}
}

function displayMessage(sender, message) {
	const messageContainer = document.getElementById("chatbotMessages");

	const messageElement = document.createElement("div");
	messageElement.innerText = message;
	messageElement.classList.add("message", `${sender}Message`);

	messageContainer.appendChild(messageElement);
	scrollChatToBottom();
}

function scrollChatToBottom() {
	const chatbotMessages = document.getElementById('chatbotMessages');
	chatbotMessages.scrollTop = chatbotMessages.scrollHeight;
}
function confirmNavigation(event) {
    if (!confirm("Do you really want to go to the home page?")) {
        event.preventDefault();
    } else {
        window.location.href = "/";
    }}


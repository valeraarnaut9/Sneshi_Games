const avatarInput =
document.getElementById("avatarInput");

const openButton =
document.getElementById("openEditProfile");


const closeButton =
document.getElementById("closeEditProfile");


const overlay =
document.getElementById("profileEditOverlay");





if(closeButton){


    closeButton.onclick = ()=>{

        overlay.classList.remove("show");

    };


}





const form =
document.getElementById("editProfileForm");


const displayInput =
document.getElementById("displayNameInput");


const bioInput =
document.getElementById("bioInput");


const confirmButton =
document.querySelector(".confirm-profile-button");


let oldDisplayName = "";
let oldBio = "";



if(openButton){

    openButton.onclick = ()=>{

        overlay.classList.add("show");


        oldDisplayName = displayInput.value;

        oldBio = bioInput.value;


        checkChanges();

    };

}


function checkChanges(){


    if(
        displayInput.value === oldDisplayName &&
        bioInput.value === oldBio
    ){

        confirmButton.classList.add("disabled");

        confirmButton.disabled = true;

    }

    else{

        confirmButton.classList.remove("disabled");

        confirmButton.disabled = false;

    }


}

if(displayInput && bioInput){


    displayInput.addEventListener(
        "input",
        checkChanges
    );


    bioInput.addEventListener(
        "input",
        checkChanges
    );


}

if(form){


form.addEventListener("submit", async(e)=>{


    e.preventDefault();

    
if(confirmButton.disabled){

    return;

}





    if(confirmButton){

        confirmButton.classList.add("loading");

        confirmButton.disabled = true;

    }





    const display_name =
    document.getElementById("displayNameInput").value;



    const bio =
    document.getElementById("bioInput").value;


const formData =
new FormData();


formData.append(
    "display_name",
    display_name
);


formData.append(
    "bio",
    bio
);


if(avatarInput && avatarInput.files[0]){

    formData.append(
        "avatar",
        avatarInput.files[0]
    );

}


    const response =
    await fetch(
    "/api/profile/edit",
    {

        method:"POST",

        body:formData

    }
);





    const data =
    await response.json();





    if(data.success){


        overlay.classList.remove("show");


        location.reload();


    }

    else{


        if(confirmButton){

            confirmButton.classList.remove("loading");

            confirmButton.disabled = false;

        }


        alert(data.message);


    }



});


}

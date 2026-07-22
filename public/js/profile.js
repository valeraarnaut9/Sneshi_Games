const openButton =
document.getElementById("openEditProfile");


const closeButton =
document.getElementById("closeEditProfile");


const overlay =
document.getElementById("profileEditOverlay");



if(openButton){


    openButton.onclick = ()=>{

        overlay.classList.add("show");

    };


}





if(closeButton){


    closeButton.onclick = ()=>{

        overlay.classList.remove("show");

    };


}





const form =
document.getElementById("editProfileForm");



if(form){


form.addEventListener("submit", async(e)=>{


    e.preventDefault();



    const confirmButton =
    document.querySelector(".confirm-profile-button");



    if(confirmButton){

        confirmButton.classList.add("loading");

        confirmButton.disabled = true;

    }





    const display_name =
    document.getElementById("displayNameInput").value;



    const bio =
    document.getElementById("bioInput").value;





    const response =
    await fetch(
        "/api/profile/edit",
        {

            method:"POST",

            headers:{

                "Content-Type":
                "application/json"

            },

            body:JSON.stringify({

                display_name,

                bio

            })

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

const express = require("express");
const path = require("path");
const { createClient } = require("@supabase/supabase-js");
const { v4: uuidv4 } = require("uuid");
const bcrypt = require("bcrypt");
const cookieParser = require("cookie-parser");

const auth = require("./middleware/auth");


const app = express();


// ---------- EJS ----------

app.set("view engine", "ejs");
app.set("views", path.join(__dirname, "views"));


// ---------- Public ----------

app.use(express.static(path.join(__dirname, "public")));


// ---------- Body ----------

app.use(express.urlencoded({ extended: true }));
app.use(express.json());


// ---------- Cookies ----------

app.use(cookieParser());


// ---------- Auth ----------

app.use(auth);


// ---------- Supabase ----------

const supabase = createClient(
    process.env.SUPABASE_URL,
    process.env.SUPABASE_KEY
);




// ---------- Главная ----------

app.get("/", (req, res) => {


    if (req.user) {

        return res.redirect(
            "/users/" + req.user.userid
        );

    }


    res.redirect("/signin");


});




// ---------- Sign In ----------

app.get("/signin", (req, res) => {


    if (req.user) {

        return res.redirect(
            "/users/" + req.user.userid
        );

    }


    res.render("signin", {

        error: null

    });


});





app.post("/signin", async (req, res) => {


    const {
        username,
        password
    } = req.body;



    if (!username || !password) {


        return res.render("signin", {

            error: "Fill all fields"

        });


    }





    const { data: user, error } = await supabase
        .from("users")
        .select(
            "userid, username, password_hash"
        )
        .eq("username", username)
        .single();





    if (error || !user) {


        return res.render("signin", {

            error: "Incorrect username or password"

        });


    }





    const passwordCorrect =
        await bcrypt.compare(
            password,
            user.password_hash
        );





    if (!passwordCorrect) {


        return res.render("signin", {

            error: "Incorrect username or password"

        });


    }





    const token = uuidv4();



    const expires = new Date();


    expires.setDate(
        expires.getDate() + 30
    );





    await supabase
        .from("sessions")
        .insert({

            userid: user.userid,

            token: token,

            device: "Unknown",

            ip: req.ip,

            expires_at: expires

        });







    res.cookie(
        "session_token",
        token,
        {

            httpOnly: true,

            maxAge:
            30 * 24 * 60 * 60 * 1000

        }
    );





    res.redirect(
        "/users/" + user.userid
    );


});





// ---------- Sign Up ----------

app.get("/signup", (req, res) => {


    res.render("signup");


});





app.post("/signup", async (req, res) => {


    const {

        username,

        display_name,

        password

    } = req.body;





    const { data: exists } =
        await supabase
            .from("users")
            .select("userid")
            .eq("username", username)
            .single();





    if (exists) {


        return res.render("signup", {

    error: "Username already exists"

});


    }





    let userid;



    while(true){


        const id =
            Math.floor(
                10000 +
                Math.random() * 90000
            );



        const { data } =
            await supabase
                .from("users")
                .select("userid")
                .eq("userid", id)
                .single();



        if(!data){

            userid = id;

            break;

        }

    }





    const hash =
        await bcrypt.hash(
            password,
            10
        );





    await supabase
        .from("users")
        .insert({

            userid,

            username,

            display_name,

            bio: "No bio",

            password_hash: hash

        });






    const token = uuidv4();



    const expires = new Date();



    expires.setDate(
        expires.getDate() + 30
    );





    await supabase
        .from("sessions")
        .insert({

            userid,

            token,

            device:"Unknown",

            ip:req.ip,

            expires_at:expires

        });





    res.cookie(
        "session_token",
        token,
        {

            httpOnly:true,

            maxAge:
            30 * 24 * 60 * 60 * 1000

        }
    );





    res.redirect(
        "/users/" + userid
    );


});







// ---------- Profile ----------

app.get("/users/:userid", async (req,res)=>{


    const userid =
        req.params.userid;




    const {data,error} =
        await supabase
        .from("users")
        .select(
            "userid, username, display_name, bio"
        )
        .eq("userid",userid)
        .single();





    if(error || !data){

        return res
        .status(404)
        .send("User not found");

    }





    const avatarPath =
    `https://guidsuqitwysbgoevmin.supabase.co/storage/v1/object/public/avatars/users-avatars/avatar_${userid}.webp`;



    const defaultAvatar =
    "https://guidsuqitwysbgoevmin.supabase.co/storage/v1/object/public/avatars/default-avatar/default_avatar.webp";





    res.render("profile",{


        username:data.username,

        display_name:data.display_name,

        bio:data.bio,

        userid:data.userid,

        avatar:avatarPath,

        defaultAvatar


    });



});





// ---------- Logout ----------

app.get("/logout", async(req,res)=>{


    const token =
        req.cookies.session_token;



    if(token){


        await supabase
            .from("sessions")
            .delete()
            .eq("token",token);


    }





    res.clearCookie(
        "session_token"
    );



    res.redirect("/signin");


});






const PORT =
process.env.PORT || 3000;



app.listen(PORT,()=>{


    console.log(
        "Server started:",
        PORT
    );


});

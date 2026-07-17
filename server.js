const express = require("express");
const { createClient } = require("@supabase/supabase-js");


const app = express();


const supabase = createClient(
    process.env.SUPABASE_URL,
    process.env.SUPABASE_KEY
);



app.get("/", (req,res)=>{
    res.send("Server online");
});



app.get("/users/:userid", async (req,res)=>{


    const userid = req.params.userid;


    const {data,error} = await supabase
        .from("users")
        .select("userid, username, created_at")
        .eq("userid", userid)
        .single();



    if(error){

        return res.status(404).json({
            error:"User not found"
        });

    }


    res.json(data);


});



const PORT = process.env.PORT || 3000;


app.listen(PORT,()=>{
    console.log(
        "Server started:",
        PORT
    );
});

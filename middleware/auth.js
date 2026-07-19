const { createClient } = require("@supabase/supabase-js");


const supabase = createClient(
    process.env.SUPABASE_URL,
    process.env.SUPABASE_KEY
);



async function auth(req, res, next) {


    const token = req.cookies.session_token;



    if (!token) {

        req.user = null;

        return next();

    }



    const { data: session, error } = await supabase
        .from("sessions")
        .select("userid, expires_at")
        .eq("token", token)
        .single();



    if (error || !session) {

        req.user = null;

        return next();

    }




    const expires =
        new Date(session.expires_at);



    if (expires < new Date()) {


        await supabase
            .from("sessions")
            .delete()
            .eq("token", token);



        res.clearCookie("session_token");


        req.user = null;

        return next();

    }




    const { data: user } = await supabase
        .from("users")
        .select(
            "userid, username, display_name"
        )
        .eq("userid", session.userid)
        .single();




    req.user = user || null;



    next();

}



module.exports = auth;

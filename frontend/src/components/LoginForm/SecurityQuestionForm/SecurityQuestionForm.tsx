import { useEffect, useState, useRef, useCallback } from 'react';
import {useLocation, useNavigate} from 'react-router-dom';
import { TextField, Button, Stack } from '@mui/material';
import sharedCSSModule from '../../shared/css/shared.module.css';
import {Simulate} from "react-dom/test-utils";
import {auth} from "../../../../firebaseconfig";
import error = Simulate.error;

export default function SecurityQuestionForm() {
    const location = useLocation();
    const { claim, email, token, uid } = location.state || {}; // Add a default empty object if location.state is null

    const [secQuestion, setSecQuestion] = useState('');
    const [loading, setLoading] = useState(true);
    const securityQuestionAnswerRef = useRef(null);
    const [responseMessage, setResponseMessage] = useState('');
    const navigate = useNavigate();
    const [response, setResponse] = useState({
        claim: '',
        email: '',
        token: '',
        uid: '',
    });

    const handleAppRedirect = async (user) => {
        console.log("handleAppRedirect", user.claimValue);
        if (user.claimValue === 'admin') {
            navigate('/home/admin/games', {
                state: {
                    email: user.email,
                    token: user.token,
                    uid: user.uid,
                },
            });
        } else if (localStorage.getItem("team") && localStorage.getItem("user")) {
            navigate('/home/gamesList', {
                state: {
                    email: user.email,
                    token: user.token,
                    uid: user.uid,
                },
            });
        } else {
            navigate("/home/addTeam");
        }
    }


    const getTeamData = async () => {
        let currentUser = auth.currentUser;
        if(currentUser){
            let idToken = currentUser.getIdToken();
            let response = await fetch("https://6418qzn2i7.execute-api.us-east-1.amazonaws.com/dev/app/team",{
                method: "GET",
                headers: {
                    authorizationToken: idToken
                }
            });
            let json = await response.json();
            console.log(json);
            if(json.status && Array.isArray(json.teamData) && json.teamData.length){
                localStorage.setItem("team", JSON.stringify(json.teamData[0]));
            }

        }
    }
    const formHandler = useCallback(
        async (event) => {
            event.preventDefault();

            const data = {
                uid: uid, // Use the uid from the location state
                question: secQuestion, // Use the fetched security question
                answer: securityQuestionAnswerRef.current?.value,
            };

            try {
                const answerresponse = await fetch('https://login-kku3a2biga-uc.a.run.app/checkanswer', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(data),
                });

                const answerresponseData = await answerresponse.json();
                console.log("answerresponseData:", answerresponseData)
                if (answerresponseData.response === 'Answer is correct.') {
                    setResponse({
                        claim: claim,
                        email: email,
                        token: token,
                        uid: uid,
                    });
                    console.log("calling team")
                    await getTeamData();
                    console.log("calling app redirect")
                    const userData = localStorage.getItem('user');
                    const userObject = JSON.parse(userData);
                    const tokenValue = userObject.token;
                    const emailValue = userObject.email;
                    const uidValue = userObject.uid;
                    const claimValue = userObject.claim;

                    await handleAppRedirect({emailValue, tokenValue, uidValue, claimValue});
                    console.log("after app redirect")
                    
                }
                 else {
                    setResponseMessage('Answer is incorrect.');
                }
            } catch (error) {
                console.error('Error occurred while making the API call:', error);
            }
        },
        [secQuestion, uid]
    );

    useEffect(() =>{
        async function fetchSecurityQuestion() {
            if (!uid) {
                // Handle the case when uid is not available (location.state is null)
                console.error('No uid available in location state.');
                setLoading(false);
                return;
            }

            const data = {
                uid: uid, // Use the uid from the location state
            };

            try {
                const response = await fetch('https://login-kku3a2biga-uc.a.run.app/get/question', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(data),
                });

                const responseData = await response.json();
                if (response.ok) {
                    setSecQuestion(responseData.response);
                    setLoading(false);
                } else {
                    // Handle error scenario if needed
                    console.error('Error occurred while fetching the security question.');
                }
            } catch (error) {
                console.error('Error occurred while making the API call:', error);
            }
        }

        fetchSecurityQuestion();
    }, [uid]); // Add uid as a dependency to the useEffect hook

    if (loading) {
        return <div>Loading...</div>; // You can show a loading indicator while waiting for the API response
    }

    return (
        <>
            <form onSubmit={formHandler} className={sharedCSSModule.login_form}>
                <Stack spacing={1}>
                    <TextField disabled value={secQuestion} fullWidth label="Security Question" id="sec_q" name="sec_q" />
                    <TextField inputRef={securityQuestionAnswerRef} fullWidth label="Security Question Answer" id="sec_q_ans" name="sec_q_ans" type="password" />
                    <Button sx={{ mb: 2, py: 1 }} type="submit" variant="contained">
                        Submit
                    </Button>
                </Stack>
            </form>
        </>
    );
}

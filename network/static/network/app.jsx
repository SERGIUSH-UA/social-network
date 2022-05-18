//import React from 'react'

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        let cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            let cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

async function getPosts(post_id) {
    const csrftoken = getCookie('csrftoken');
    let config = {
        params: {
            id: post_id
        },
        headers: {
            'Accept': 'application/json',
            'X-CSRFToken': csrftoken
        }
    }
    await axios.get('/posts', config).then((response) => {
        console.log(response);
        return response;
    }).catch(function (error) {
        return error;
    });
}

function Post(props) {

    const [body, setBody] = React.useState("");
    const [error, setError] = React.useState("");
    const [liked, setLiked] = React.useState(props.post.liked);


    const sendComment = async () => {
        let formField = new FormData();
        const csrftoken = getCookie('csrftoken');
        const p_url = document.querySelector("#comment-form").dataset.url;
        let a_url = document.querySelector("#post-form").dataset.url;
        a_url = a_url + "/" +props.post.id;
        if (body.length < 3) {
            setError("Must be more than 3 symbols!");
            return;
        }
        if (body.length > 128) {
            setError("Must be less than 128 symbols!");
            return;
        }
        formField.append("post_id", props.post.id);
        formField.append("body", body);
        formField.append("csrftoken", csrftoken);

        await axios({
            method: "post",
            url: p_url,
            data: formField,
            headers: {
                'Accept': 'application/json',
                'Content-Type': 'application/json',
                'X-CSRFToken': csrftoken
            }
        }).then((response) => {
            console.log(response);
            axios.get(a_url).then((response_p) => {
                props.updatePost(props.index, response_p.data);
                }
            ).catch()
        }).catch(function (error) {
            // handle error
            console.log(error);
            setError(error.toString())
        }).finally(() => {
            setBody("");
        });

    }

    const sendLike = async () => {
        let formField = new FormData();
        const csrftoken = getCookie('csrftoken');
        const p_url = document.querySelector("#like-form").dataset.url;
        let a_url = document.querySelector("#post-form").dataset.url;
        a_url = a_url + "/" +props.post.id;
        formField.append("post_id", props.post.id);
        formField.append("csrftoken", csrftoken);

        await axios({
            method: "post",
            url: p_url,
            data: formField,
            headers: {
                'Accept': 'application/json',
                'Content-Type': 'application/json',
                'X-CSRFToken': csrftoken
            }
        }).then((response) => {
            console.log(response);
            axios.get(a_url).then((response_p) => {
                    props.updatePost(props.index, response_p.data);
                }
            ).catch()
        }).catch(function (error) {
            // handle error
            console.log(error);
            setError(error.toString())
        }).finally(() => {
            setBody("");
        });

    }

    return (
        <div>
            <div className="timeline-time">
                <span className="date">{props.post.date}</span>
                <span className="time">{props.post.time}</span>
            </div>
            <div className="timeline-icon">
                <a href="#">&nbsp;</a>
            </div>
            <div className="timeline-body">
                <div className="timeline-header">
                    <span className="userimage">
                        <img src={props.post.avatar}
                             alt=""/></span>
                    <span className="username"><a href="#">{props.post.ownerName}</a> <small/></span>
                    <span className="pull-right text-muted">18 Views</span>
                </div>
                <div className={props.post.truncate ? 'timeline-content truncate' : 'timeline-content'}>
                    <p>
                        {props.post.body}
                    </p>
                    {props.post.body.length > 250 && <button onClick={() => {
                        props.deleteTrunk(props.index)
                    }} className="read-more">{props.post.truncate ? "Read more.." : "Minimize"}</button>}
                </div>
                <div className="timeline-likes">
                    <div className="stats-right">
                        <span className="stats-text">259 Shares</span>
                        <span className="stats-text">{props.post.comments} Comments</span>
                    </div>
                    <div className="stats">
                                    <span className="fa-stack fa-fw stats-icon">
                                    <i className="fa fa-circle fa-stack-2x text-danger"/>
                                    <i className="fa fa-heart fa-stack-1x fa-inverse t-plus-1"/>
                                    </span>
                        <span className="fa-stack fa-fw stats-icon">
                                    <i className="fa fa-circle fa-stack-2x text-primary"/>
                                    <i className="fa fa-thumbs-up fa-stack-1x fa-inverse"/>
                                    </span>
                        <span className="stats-total">{props.post.likes}</span>
                    </div>
                </div>
                <div className="timeline-footer">
                    <a onClick={sendLike} className={"m-r-15 text-inverse-lighter cursor-pointer " + (props.post.liked ? "liked" : "")}><i
                        className="fa fa-thumbs-up fa-fw fa-lg m-r-3"/> Like</a>
                    <a onClick={() => {
                        props.activeComment(props.index)
                    }} className="m-r-15 text-inverse-lighter cursor-pointer"><i
                        className="fa fa-comments fa-fw fa-lg m-r-3"/> Comment</a>
                    <a className="m-r-15 text-inverse-lighter cursor-pointer"><i
                        className="fa fa-share fa-fw fa-lg m-r-3 "/> Share</a>
                </div>
                {props.post.actComment && <div className="timeline-comment-box">
                    <div className="user"><img src={props.post.comment_avatar} alt=""/></div>
                    <div className="input">
                        <div>
                            <div className="input-group">
                                <input type="text" className="form-control rounded-corner"
                                       placeholder="Write a comment..." value={body} minLength="3"
                                       onChange={(e) => {
                                           setBody(e.target.value);
                                           setError("");
                                       }
                                       }/>
                                <small className="text-danger">{error}</small>
                                <span className="input-group-btn p-l-10">
                                          <button  onClick={sendComment}
                                                  className="btn btn-info f-s-12 rounded-corner">Comment</button>
                                          </span>
                            </div>
                        </div>
                    </div>
                </div>}
            </div>
        </div>
    );
}

function Timeline(props) {
    const [page, setPage] = React.useState(-10);
    const [posts, setPosts] = React.useState([]);
    const [fetching, setFetching] = React.useState(true);
    const [fetchingNew, setFetchingNew] = React.useState(false);

    const updateNewPost = () => {
        setFetchingNew(true);
    }
    React.useEffect(() => {
        document.addEventListener('scroll', scrollHandler);
        return function () {
            document.removeEventListener('scroll', scrollHandler);
        };
    }, []);

    const scrollHandler = (e) => {
        if (e.target.documentElement.scrollHeight - (e.target.documentElement.scrollTop + window.innerHeight) < 100
            && page !== 0) {
            setFetching(true);
        }
    };

    React.useEffect(() => {
        if (fetchingNew) {
            const csrftoken = getCookie('csrftoken');
            let idPost = -10;
            if (posts.length !== 0) {
                idPost = posts[0].id;
            }
            let config = {
                params: {
                    id: idPost,
                    eq: 'gt'
                },
                headers: {
                    'Accept': 'application/json',
                    'X-CSRFToken': csrftoken
                }
            }
            axios.get('/posts', config).then((response) => {
                let tmplPosts = [...response.data];
                tmplPosts.forEach((el) => {
                    el.actComment = false;
                })
                setPosts([...tmplPosts, ...posts]);
            }).catch(function (error) {
                console.log(error);
            }).finally(() => {
                setFetchingNew(false);
            });
        }
    }, [fetchingNew]);

    React.useEffect(() => {
        if (fetching) {
            const csrftoken = getCookie('csrftoken');
            let config = {
                params: {
                    id: page,
                    eq: 'lt'
                },
                headers: {
                    'Accept': 'application/json',
                    'X-CSRFToken': csrftoken
                }
            }
            axios.get('/posts', config).then((response) => {
                let tmplPosts = [...response.data];
                tmplPosts.forEach((el) => {
                    el.actComment = false;
                })
                setPosts([...posts, ...tmplPosts]);
                setPage(response.headers.last_id);
            }).catch(function (error) {
                console.log(error);
            }).finally(() => {
                setFetching(false);
            });
        }
    }, [fetching]);

    const truncate = (index) => {
        let tmplPost = [...posts];
        tmplPost[index].truncate = !tmplPost[index].truncate;
        setPosts(tmplPost);
    }

    const activeComment = (index) => {
        let tmplPost = [...posts];
        tmplPost[index].actComment = !tmplPost[index].actComment;
        setPosts(tmplPost);
    }

    const updatePost = (index, post) => {
        let tmplPosts = [...posts];
        let tmplPost = tmplPosts[index];
        Object.assign(tmplPost, post);
        setPosts(tmplPosts);
    }


    return (<div>
            <PostForm updateNewPost={updateNewPost}/>
            <ul className="timeline">
                {posts.map((post, index) =>
                    <li className={post.new ? 'animated-add-new' : 'animated-add'} key={index}>
                        <Post post={post} deleteTrunk={truncate} activeComment={activeComment} index={index}
                        updatePost={updatePost}/>
                    </li>
                )}
            </ul>
        </div>
    );
}

function PostForm(props) {
    const [body, setBody] = React.useState("");
    const [error, setError] = React.useState("");

    const sendPost = async () => {
        let formField = new FormData();
        const csrftoken = getCookie('csrftoken');
        const p_url = document.querySelector("#post-form").dataset.url;
        if (body.length < 5) {
            setError("Must be more than 5 symbols!");
            return;
        }
        if (body.length > 512) {
            setError("Must be less than 512 symbols!");
            return;
        }
        formField.append("body", body);
        formField.append("csrftoken", csrftoken);

        await axios({
            method: "post",
            url: p_url,
            data: formField,
            headers: {
                'Accept': 'application/json',
                'Content-Type': 'application/json',
                'X-CSRFToken': csrftoken
            }
        }).then((response) => {
            console.log(response)
        }).catch(function (error) {
            // handle error
            console.log(error);
            setError(error.toString())
        }).finally(() => {
            setBody("");
            props.updateNewPost();
        });

    }

    return (<div className="panel-activity__status">
       <textarea name="body" placeholder="Share what you've been up to..."
                 onChange={((event) => {
                     setBody(event.target.value);
                     setError("");
                 })} className="form-control" value={body} minLength={5}/>
        <small id="formHelp" className="text-danger">{error}</small>
        <div className="actions">
            <div className="btn-group">
                <button type="button" className="btn-link" title="" data-toggle="tooltip"
                        data-original-title="Post an Image">
                    <i className="fa fa-image"/>
                </button>
                <button type="button" className="btn-link" title="" data-toggle="tooltip"
                        data-original-title="Post an Video">
                    <i className="fa fa-video-camera"/>
                </button>
                <button type="button" className="btn-link" title="" data-toggle="tooltip"
                        data-original-title="Post an Idea">
                    <i className="fa fa-lightbulb-o"/>
                </button>
                <button type="button" className="btn-link" title="" data-toggle="tooltip"
                        data-original-title="Post an Question">
                    <i className="fa fa-question-circle-o"/>
                </button>
            </div>
            <button onClick={sendPost} className="btn  btn-rounded btn-info">
                Post
            </button>
        </div>
    </div>);
}

function App() {

    return (<div>
        <Timeline/>
    </div>);
}


ReactDOM.render(<App/>, document.querySelector("#timeline"));
//ReactDOM.render(<Timeline/>, document.querySelector("#timeline"));
//ReactDOM.render(<PostForm/>, document.querySelector("#post-form"));
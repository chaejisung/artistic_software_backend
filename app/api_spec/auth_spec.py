class AuthSpec:
    @staticmethod
    def auth_google_login():
        spec = {
            "summary": "구글 로그인 화면으로 넘어가는 엔드포인트",
            "description": 
                """
                    해당 api에 요청 시 구글 로그인 화면으로 넘어가는 307 리다이렉트 응답 반환 <br><br> 
                    구글 로그인 절차 마친 후, localhost:3000/auth/google/callback의 쿼리파라미터로 응답
                """,
            "operation_id": "auth_google_login",
            "responses": {
                200: {"description": "해당 응답 존재X"},
                307: {"description": "구글 리다이렉트 응답"}
            }
        }
        return spec

    @staticmethod
    def auth_google_callback():
        spec = {
            "summary": "구글 인증 코드를 첨부해 요청하면 이후 회원가입, 로그인 절차를 처리하는 엔드포인트",
            "description": 
                """
                    구글 인증 코드를 첨부해 요청하면 이후 회원가입, 로그인 절차를 처리하는 엔드포인트 <br><br>  
                    회원가입, 로그인 처리 후 메시지, action_type(register, login), 사용자 이름 반환
                """,
            "operation_id": "auth_google_callback",
            "responses": {
                200: {
                    "description": "메시지, action_type(register, login), 사용자 이름",
                    "content": {
                            "application/json": {
                                "examples": {
                                    "회원가입 예시": {
                                        "summary": "회원가입 예시",
                                        "value": {
                                            "message": "register process is complete",
                                            "action_type": "register",
                                            "username": "test1"
                                        }
                                    },
                                    "로그인 예시": {
                                        "summary": "로그인 예시",
                                        "value": {
                                            "message": "login process is complete",
                                            "action_type": "login",
                                            "username": "test1"
                                        }
                                    }
                                }
                            }
                        }
                    },
                }
            }
        return spec
    
    @staticmethod
    def auth_kakao_login():
        spec = {
            "summary": "카카오 로그인 화면으로 넘어가는 엔드포인트",
            "description": 
                """
                    해당 api에 요청 시 카카오 로그인 화면으로 넘어가는 307 리다이렉트 응답 반환 <br><br> 
                    카카오 로그인 절차 마친 후, localhost:3000/auth/kakao/callback의 쿼리파라미터로 응답
                """,
            "operation_id": "auth_kakao_login",
            "responses": {
                200: {"description": "해당 응답 존재X"},
                307: {"description": "카카오 리다이렉트 응답"}
            }
        }
        return spec

    @staticmethod
    def auth_kakao_callback():
        spec = {
            "summary": "카카오 인증 코드를 첨부해 요청하면 이후 회원가입, 로그인 절차를 처리하는 엔드포인트",
            "description": 
                """
                    카카오 인증 코드를 첨부해 요청하면 이후 회원가입, 로그인 절차를 처리하는 엔드포인트 <br><br>  
                    회원가입, 로그인 처리 후 메시지, action_type(register, login), 사용자 이름 반환
                """,
            "operation_id": "auth_kakao_callback",
            "responses": {
                200: {
                    "description": "메시지, action_type(register, login), 사용자 이름",
                    "content": {
                            "application/json": {
                                "examples": {
                                    "회원가입 예시": {
                                        "summary": "회원가입 예시",
                                        "value": {
                                            "message": "register process is complete",
                                            "action_type": "register",
                                            "username": "test1"
                                        }
                                    },
                                    "로그인 예시": {
                                        "summary": "로그인 예시",
                                        "value": {
                                            "message": "login process is complete",
                                            "action_type": "login",
                                            "username": "test1"
                                        }
                                    }
                                }
                            }
                        }
                    },
            }
        }
        return spec

    @staticmethod
    def auth_google_logout():
        spec = {
            "summary": "미완성 api"
        }
        return spec
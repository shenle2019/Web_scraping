package com.shenjiahang.netapp.model;

/** /login 返回：字段名必须和 json key 完全一致，否则 Gson 静默给 null */
public class LoginResult extends BaseResp {
    public String token;
    public String user;
}

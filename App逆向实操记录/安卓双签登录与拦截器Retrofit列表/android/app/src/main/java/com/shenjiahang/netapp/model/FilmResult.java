package com.shenjiahang.netapp.model;

import java.util.ArrayList;

/** /films 返回：data 是数组，必须用带泛型的集合类接收 */
public class FilmResult extends BaseResp {
    public ArrayList<Film> data;
}

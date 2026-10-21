package com.shenjiahang.netapp.ui;

import android.content.Context;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.BaseAdapter;
import android.widget.ImageView;
import android.widget.TextView;

import com.bumptech.glide.Glide;
import com.shenjiahang.netapp.R;
import com.shenjiahang.netapp.model.Film;

import java.util.ArrayList;
import java.util.List;
import java.util.Locale;

/**
 * BaseAdapter 四件套 + convertView 复用（课件示例每次 inflate，这里补上标准写法）。
 */
public class FilmAdapter extends BaseAdapter {

    private final List<Film> data = new ArrayList<>();
    private final LayoutInflater inflater;

    public FilmAdapter(Context context) {
        inflater = LayoutInflater.from(context);
    }

    public void setData(List<Film> films) {
        data.clear();
        if (films != null) {
            data.addAll(films);
        }
        notifyDataSetChanged();
    }

    @Override
    public int getCount() {
        return data.size();
    }

    @Override
    public Film getItem(int position) {
        return data.get(position);
    }

    @Override
    public long getItemId(int position) {
        return data.get(position).id;
    }

    @Override
    public View getView(int position, View convertView, ViewGroup parent) {
        ViewHolder holder;
        if (convertView == null) {
            convertView = inflater.inflate(R.layout.item_film, parent, false);
            holder = new ViewHolder();
            holder.cover = convertView.findViewById(R.id.iv_cover);
            holder.title = convertView.findViewById(R.id.tv_title);
            holder.meta = convertView.findViewById(R.id.tv_meta);
            holder.score = convertView.findViewById(R.id.tv_score);
            convertView.setTag(holder);
        } else {
            holder = (ViewHolder) convertView.getTag();
        }

        Film film = getItem(position);
        holder.title.setText(film.title);
        holder.meta.setText(String.format(Locale.CHINA, "%s · %s · 导演 %s",
                film.year, film.genre, film.director));
        holder.score.setText(String.format(Locale.CHINA, "%.1f", film.score));

        Glide.with(holder.cover)
                .load(film.cover)
                .placeholder(R.drawable.bg_poster)
                .error(R.drawable.bg_poster)
                .centerCrop()
                .into(holder.cover);

        return convertView;
    }

    private static class ViewHolder {
        ImageView cover;
        TextView title;
        TextView meta;
        TextView score;
    }
}

package com.example.animewallpaper

import android.app.WallpaperManager
import android.graphics.BitmapFactory
import android.os.Bundle
import android.widget.Button
import android.widget.ImageView
import androidx.appcompat.app.AppCompatActivity
import okhttp3.OkHttpClient
import okhttp3.Request
import java.io.IOException

class MainActivity : AppCompatActivity() {
    private val client = OkHttpClient()
    private val imageUrls = mutableListOf<String>()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        val imgView1 = findViewById<ImageView>(R.id.image1)
        val imgView2 = findViewById<ImageView>(R.id.image2)
        val imgView3 = findViewById<ImageView>(R.id.image3)
        val setButton = findViewById<Button>(R.id.setButton)

        // Fetch three images from the API (placeholder function)
        fetchImages { urls ->
            imageUrls.addAll(urls)
            // Load images into ImageViews using a simple method (could use Glide in production)
            loadImageIntoView(urls[0], imgView1)
            loadImageIntoView(urls[1], imgView2)
            loadImageIntoView(urls[2], imgView3)
        }

        setButton.setOnClickListener {
            // For simplicity, use the first image as selected
            val selectedUrl = imageUrls.getOrNull(0)
            selectedUrl?.let { setWallpaperFromUrl(it) }
        }
    }

    private fun fetchImages(callback: (List<String>) -> Unit) {
        // This is a placeholder implementation. In a real app, you would call the anime API
        // with width/height parameters. Here we just use three static URLs.
        val dummyUrls = listOf(
            "https://i.waifu.pics/HaDv5Z-.jpg",
            "https://i.waifu.pics/2bXc3Y-.jpg",
            "https://i.waifu.pics/3kL9Qz-.jpg"
        )
        callback(dummyUrls)
    }

    private fun loadImageIntoView(url: String, imageView: ImageView) {
        // Simple synchronous download (not for production). In real code use Glide or Coil.
        val request = Request.Builder().url(url).build()
        client.newCall(request).execute().use { response ->
            if (!response.isSuccessful) return
            val bytes = response.body?.bytes() ?: return
            val bitmap = BitmapFactory.decodeByteArray(bytes, 0, bytes.size)
            runOnUiThread { imageView.setImageBitmap(bitmap) }
        }
    }

    private fun setWallpaperFromUrl(url: String) {
        val request = Request.Builder().url(url).build()
        client.newCall(request).enqueue(object : okhttp3.Callback {
            override fun onFailure(call: okhttp3.Call, e: IOException) {
                e.printStackTrace()
            }
            override fun onResponse(call: okhttp3.Call, response: okhttp3.Response) {
                val bytes = response.body?.bytes() ?: return
                val bitmap = BitmapFactory.decodeByteArray(bytes, 0, bytes.size)
                val wm = WallpaperManager.getInstance(applicationContext)
                try {
                    wm.setBitmap(bitmap)
                } catch (e: IOException) {
                    e.printStackTrace()
                }
            }
        })
    }
}

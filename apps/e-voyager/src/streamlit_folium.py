"""Browser stand-in for streamlit-folium: renders the folium map as static HTML (custom components can't run in stlite)."""
import streamlit.components.v1 as components


def st_folium(fig, width=700, height=500, **kwargs):
    components.html(fig.get_root().render(), height=height, scrolling=False)
    return {}


folium_static = st_folium

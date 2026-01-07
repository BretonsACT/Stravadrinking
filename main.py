import streamlit as st
from supabase import create_client, Client
from st_supabase_connection import SupabaseConnection

# 1. Inicializar conexión
# Usamos el conector oficial de Streamlit para Supabase
#conn = st.connection("supabase", type=SupabaseConnection)

# Cliente para operaciones avanzadas como subir fotos
#url = st.secrets["SUPABASE_URL"]
#key = st.secrets["SUPABASE_KEY"]
#supabase: Client = create_client(url, key)

st.title("🍻 Drink-In: El Strava de las Cañas")

# --- FORMULARIO PARA REGISTRAR ---
with st.expander("➕ Registrar lo que estoy bebiendo"):
    with st.form("drink_form"):
        user = st.text_input("Tu nombre")
        drink = st.text_input("¿Qué es?")
        alc = st.slider("% Alcohol", 0.0, 40.0, 5.0)
        foto = st.file_uploader("Foto del trago", type=['jpg', 'png'])
        
        if st.form_submit_button("Publicar 🚀"):
            img_url = ""
            if foto:
                # Subir foto al storage
                path = f"public/{foto.name}"
                supabase.storage.from_("bebidas").upload(path, foto.getvalue())
                img_url = supabase.storage.from_("bebidas").get_public_url(path)
            
            # Insertar datos en la tabla
            conn.query("*", table="drinks", ttl=0).insert({
                "user_name": user,
                "drink_name": drink,
                "alcohol_pct": alc,
                "image_url": img_url
            }).execute()
            st.success("¡Registrado en la nube!")
            st.rerun()

# --- FEED SOCIAL REAL ---
st.subheader("📱 Actividad Reciente")
# Consultamos los datos de la base de datos
data = conn.query("*", table="drinks", ttl="0").execute()

if data.data:
    for row in reversed(data.data):
        with st.container(border=True):
            col1, col2 = st.columns([1, 2])
            with col1:
                if row['image_url']:
                    st.image(row['image_url'])
                else:
                    st.write("🍷 Sin foto")
            with col2:
                st.write(f"**{row['user_name']}** está bebiendo **{row['drink_name']}**")
                st.write(f"🔥 {row['alcohol_pct']}% de alcohol")
                
                # Botón de Kudos funcional
                if st.button(f"🙌 Kudos ({row['kudos']})", key=f"k_{row['id']}"):
                    conn.table("drinks").update({"kudos": row['kudos'] + 1}).eq("id", row['id']).execute()
                    st.rerun()

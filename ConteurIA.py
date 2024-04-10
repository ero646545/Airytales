import os
import flet as ft
from groq import Groq
import itertools
import time
import pyttsx3
from pygame import mixer
import tempfile
client = Groq(
    api_key="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",
)
current_filename = None
AutoRead=False
def get_contes_list():
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": "Tu es un conteur de contes de fée classique de qualité. Tu propose 5 titres de conte classique en liste python au format['titre1','titre2'].",
                }
            ],
            model="mixtral-8x7b-32768",  max_tokens=100,
        )

        chat = chat_completion.choices[0].message.content
        liste = []
        try:
            start_index = chat.index('[') + 1
            end_index = chat.index(']')
            list_str = chat[start_index:end_index]
            list_elements = list_str.split(',')
            for j in range(len(list_elements)):
                list_elements[j] = list_elements[j].strip()
            liste.extend(list_elements)
        except ValueError:
            return get_contes_list()
        #print(liste)
        return liste

def main(page: ft.Page):
    key_iter = itertools.count()

    def show_credit_page():
        page.launch_url("https://www.youtube.com/channel/UCsdlcZz0-ItfaXaPoA3iQfg")
        print("Conteur en IA provided by groq by Ero René Meng ")
        

    def add_message(message):
        text_key = f"text_{next(key_iter)}"
        text = ft.Text(message, color=ft.colors.BLACK, key=text_key)
        chat_container.controls.append(text)
        chat_container.scroll_to(key=text_key, duration=1000)
        chat_container.update()

    def dell_message():
        chat_container.controls.clear()
        chat_container.update()
        mixer.init()
        mixer.music.stop()
        time.sleep(1)
        liste_contes = get_contes_list()
        contes_message = '\n'.join(f"{i+1}. {conte}" for i, conte in enumerate(liste_contes))
        add_message(contes_message)
        update_buttons(buttons, liste_contes)  # Update this line

    def update_buttons(buttons, liste_contes):
        buttons.clear()
        for i in range(len(liste_contes)):
            btn = ft.ElevatedButton(f"Conte {i+1}", on_click=lambda e, i=i: button_clicked(e, liste_contes))
            buttons.append(btn)
        for btn in buttons:
            btn.disabled = False
        del_button.disabled = False
        page.update()
        return buttons    
    
    def audio(lecture=None):
        global current_filename
        page.update()
        chat_container.update()
        mixer.init()
        if mixer.music.get_busy():
            mixer.music.stop()

        if len(chat_container.controls) > 3 and lecture is not None:
            engine = pyttsx3.init()

            filename = os.path.join(tempfile.gettempdir(),'output.wav')
            file_index = 1
            while os.path.isfile(filename):
                filename = f'output{file_index}.wav'
                file_index += 1
            engine.save_to_file(lecture, filename)
            engine.runAndWait()
            mixer.init()
            mixer.music.load(filename)

            if current_filename is not None and os.path.isfile(current_filename):
                os.remove(current_filename)

            mixer.music.play()
            current_filename = filename
    def toggle_auto_read(e):
            global AutoRead
            if AutoRead ==True:
                AutoRead=False
            else:
              AutoRead=True
            mixer.init()
            if mixer.music.get_busy():
                mixer.music.stop()
            page.update()
            
        
    def button_clicked(e, liste_contes):
            button = e.control
            button_index = buttons.index(e.control)
            
            conte_choisi = liste_contes[button_index]
            
            for btn in buttons:
                btn.disabled = True
            audio_button.disabled = True
            del_button.disabled = True
            page.update()
            add_message(f"Je choisis le conte {conte_choisi}.")
            
            chat_completion = client.chat.completions.create(
                messages=[
                    {
                        "role": "user",
                        "content": f"Tu es un conteur Français de contes de fée classique de qualité. Tu racontes de manière épique et drôle le conte suivant: {conte_choisi} en précisant l'auteur du conte",
                    }
                ],
                model="mixtral-8x7b-32768",
            )
            
            lecture=chat_completion.choices[0].message.content
            add_message(lecture)
            time.sleep(1)

            
            liste_contes = get_contes_list()
            update_buttons(buttons, liste_contes)
            contes_message = '\n'.join(f"{i+1}. {conte}" for i, conte in enumerate(liste_contes))
            add_message(contes_message)
            time.sleep(1)
            if AutoRead==True:
                audio(lecture)  # Call the audio function with the lecture argument
            
            buttons.clear()
            for i in range(len(liste_contes)):
                btn = ft.ElevatedButton(f"Conte {i+1}", on_click=lambda e, i=i: button_clicked(e, liste_contes))
                buttons.append(btn)
            

            for btn in buttons:
                btn.disabled = False
            audio_button.disabled = False
            del_button.disabled = False
            page.update()
            


    
    chat_container = ft.Column(
        spacing=10,
        height=300,
        width=page.window_width,
        scroll=ft.ScrollMode.ALWAYS,
        controls=[],
    )
    
   
    liste_contes = get_contes_list()
    contes_message = '\n'.join(f"{i+1}. {conte}" for i, conte in enumerate(liste_contes))
    buttons = []
    for i in range(len(liste_contes)):
        btn = ft.ElevatedButton(f"Conte {i+1}", on_click=lambda e, conte=liste_contes[i]: button_clicked(e, conte))
        buttons.append(btn)
    audio_button = ft.Switch(label="Auto Read", on_change=toggle_auto_read)
    del_button = ft.ElevatedButton("Clear Chat", on_click=lambda e,: dell_message())
    page.add(
        ft.Column([
            ft.Row([
                ft.Column([ft.Text("Conteur infatigable", size=24, weight=ft.FontWeight.BOLD)], expand=True),
                ft.ElevatedButton("Credit", on_click=show_credit_page),
                del_button,
                audio_button,
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ft.Divider(),
            ft.Container(chat_container, border=ft.border.all(1)),
            ft.Row(buttons, alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
        ], scroll="none")
    )

    buttons = update_buttons(buttons, liste_contes)
    
    add_message(contes_message)



if __name__ == "__main__":
    ft.app(target=main)




 

import edgeiq
import numpy as np
import cv2
import pickle
import face_recognition

def main():
    text = "Facial Recognition"
    try:
        print("status", "loading encodings + face detector...")
        data = pickle.loads(open("encodings.pickle", "rb").read())

        image_paths = sorted(list(edgeiq.list_images("images/")))
        print("Images:\n{}\n".format(image_paths))

        with edgeiq.Streamer(queue_depth=len(image_paths), inter_msg_time=3) as streamer:
            for image_path in image_paths:
                image = cv2.imread(image_path)
                rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                face_locations = face_recognition.face_locations(rgb)
                face_encodings = face_recognition.face_encodings(rgb, face_locations)

                face_names = []
                for face_encoding in face_encodings:
                    # See if the face is a match for the known face(s)
                    matches = face_recognition.compare_faces(data["encodings"], face_encoding)
                    name = "Unknown"

                    face_distances = face_recognition.face_distance(data["encodings"], face_encoding)

                    # the smallest distance is the closest to the encoding
                    minDistance = min(face_distances)

                    # save the name if the distance is below the tolerance
                    if minDistance < 0.6:
                        idx = np.where(face_distances == minDistance)[0][0]
                        name = data["names"][idx]
                    else:
                        name = "Unknown"

                    face_names.append(name)

                # Display the results
                for (top, right, bottom, left), name in zip(face_locations, face_names):
                    # Draw a box around the face
                    cv2.rectangle(image, (left, top), (right, bottom), (0, 0, 255), 2)

                    # Draw a label with a name below the face
                    cv2.rectangle(image, (left, bottom - 20), (right, bottom), (0, 0, 255), cv2.FILLED)
                    font = cv2.FONT_HERSHEY_SIMPLEX
                    cv2.putText(image, name, (left + 6, bottom - 3), font, 0.75, (0, 255, 0), 2)
 
                streamer.send_data(image, text)
            streamer.wait()
    finally:
         print("Program Ending")

if __name__ == "__main__":
    main()

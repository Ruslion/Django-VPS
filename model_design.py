
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers

from tensorflow.keras.layers.experimental import preprocessing

def model_design(EPOCHS, x_train, y_train, x_test, y_test, class_weights_dict):
    normal_layer = preprocessing.Normalization()
    normal_layer.adapt(x_train)
    
    inputs = keras.Input(shape=(x_train.shape[1],x_train.shape[2]), name='Input')

    x = normal_layer(inputs)
    x = layers.LSTM(x_train.shape[2], activation="relu", return_sequences=True)(x)
    x = layers.LSTM(x_train.shape[2], activation="relu", return_sequences=True)(x)
    x = layers.LSTM(x_train.shape[2], activation="relu")(x)
    # x = layers.Dense(x_train.shape[2] // 2, activation="relu")(x)
    # x = layers.Dense(x_train.shape[2] // 2, activation="relu")(x)
    # x = layers.Dense(x_train.shape[2] // 2, activation="relu")(x)
    
    output_layer = layers.Dense(len(class_weights_dict), name='output', activation='softmax' ) (x)
    # output_layer = layers.Dense(1, name='output', activation='softmax') (x)
    
    model = keras.Model(
                    inputs=inputs,
                    outputs=output_layer
                    )
    
    model.compile(
        optimizer=keras.optimizers.Adam(learning_rate=0.00001),
        loss={
            "output": keras.losses.CategoricalCrossentropy(name="loss")
            },
        weighted_metrics = [keras.losses.CategoricalCrossentropy(name="cat_cross"),
                  keras.metrics.AUC(name="PR", curve='PR')],
        # metrics=[keras.metrics.CategoricalAccuracy(name="cat_acc", dtype=None),
        #           keras.metrics.AUC(name="auc")]
            
                )

    history = model.fit(
        {"Input": x_train},
        {"output":y_train},
        # class_weight=class_weights_dict,
        callbacks=[tf.keras.callbacks.EarlyStopping(monitor='val_PR', patience=20, mode='max', restore_best_weights=True)],
        epochs=EPOCHS,
        validation_data = (x_test, y_test),
        verbose=0
            )

    return model, history
    
    
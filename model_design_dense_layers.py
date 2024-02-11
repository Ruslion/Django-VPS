
import tensorflow as tf
from tensorflow import keras
from keras import layers

from keras.layers.experimental import preprocessing

def model_design(EPOCHS,  x_train, y_train, x_test, y_test, class_weights_dict):
    normal_layer = preprocessing.Normalization()
    normal_layer.adapt(x_train)
    
    num_features = x_train.shape[1]

    inputs = keras.Input(shape=(num_features), name='Input')

    x = normal_layer(inputs)

    x = layers.Dense(num_features * 10, activation="leaky_relu")(x)
    
    x = layers.Dense(num_features * 9, activation="leaky_relu")(x)

    x = layers.Dense(num_features * 8, activation="leaky_relu")(x)

    x = layers.Dense(num_features * 7, activation="leaky_relu")(x)

    # x = layers.Dense(num_features * 3, activation="tanh")(x)

    # x = layers.Dense(num_features * 2, activation="tanh")(x)

    

    
    # x = layers.Dense(num_features * 2, activation="leaky_relu")(x)

    # x = layers.Dense(num_features, activation="leaky_relu")(x)

    # x = layers.Dense(num_features // 2, activation="leaky_relu")(x)

    # x = layers.Dense(num_features // 4, activation="leaky_relu")(x)
    # x = layers.Dense(num_features // 8, activation="leaky_relu")(x)
    
    # x = layers.Dense(num_features // 16, activation="leaky_relu")(x)
    
    output_layer = layers.Dense(len(class_weights_dict), name='output', activation='softmax' ) (x)
    # output_layer = layers.Dense(1, name='output', activation='softmax') (x)
    
    model = keras.Model(
                    inputs=inputs,
                    outputs=output_layer
                    )
    
    model.compile(
        optimizer=keras.optimizers.Adam(learning_rate=1e-5),
        loss={
            "output": keras.losses.CategoricalCrossentropy(name="loss")
            },
        weighted_metrics = [keras.losses.CategoricalCrossentropy(name="cat_cross"),
                #   keras.metrics.AUC(name="PR", curve='PR', num_thresholds=1000),
                  keras.metrics.SensitivityAtSpecificity(0.85, name="sens_at_spec", num_thresholds=1000),],
        
            
                )

    history = model.fit(
        {"Input": x_train},
        {"output":y_train},
        # class_weight=class_weights_dict,
        # batch_size=8,
        callbacks=[tf.keras.callbacks.EarlyStopping(monitor='val_sens_at_spec', patience=100, restore_best_weights=True)],
        epochs=EPOCHS,
        validation_data = (x_test, y_test),
        verbose=0
            )

    return model, history
    
    
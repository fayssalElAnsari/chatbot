import React from 'react'
import * as Slider from '@radix-ui/react-slider';
import * as Label from '@radix-ui/react-label';
import * as Form from '@radix-ui/react-form';

import './styles.css';

function Admin() {
    return (
        <div style={{ display: 'flex', padding: '0 20px', flexWrap: 'wrap', gap: 15, alignItems: 'center' }}>
            <Form.Root className='FormRoot'>
                <Form.Field className="FormField" name="temperature">
                    <div style={{ display: 'flex', alignItems: 'baseline', justifyContent: 'space-between' }}>
                        <Form.Label className="FormLabel">temperature</Form.Label>
                        <Form.Message className="FormMessage" match="valueMissing">
                            Default temperature
                        </Form.Message>
                    </div>
                </Form.Field>


                <Form.Submit asChild>
                    <button className="Button" style={{ marginTop: 10 }}>
                        Update Settings
                    </button>
                </Form.Submit>

            </Form.Root>
            <form>
                <Label.Root className="LabelRoot" htmlFor="temperature_slider">
                    Temperature
                </Label.Root>

                <Slider.Root id='temperature_slider' className="SliderRoot" defaultValue={[1]} max={2} step={0.01} min={0}>
                    <Slider.Track className="SliderTrack">
                        <Slider.Range className="SliderRange" />
                    </Slider.Track>
                    <Slider.Thumb className="SliderThumb" aria-label="Temperature" />
                </Slider.Root>
            </form>
        </div>
    )
}

export default Admin